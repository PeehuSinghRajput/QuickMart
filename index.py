import speech_recognition as sr
import sqlite3
from flask import Flask, request, jsonify, send_from_directory, render_template
import random
import time
from datetime import datetime
from models import Product, Order
from word2number import w2n
import recommendation


app = Flask(__name__)

def init_db():
    Product.create_table()
    Order.create_table()

def execute_query(query, params=()):
    connection = sqlite3.connect('kirana_store.db')  
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    connection.close()

def fetch_query(query, params=()):
    connection = sqlite3.connect('kirana_store.db')  
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    connection.close()
    return result

def populate_dummy_data():
    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Products")
    if cursor.fetchone()[0] == 0:
        products = [
            ("Sugar", "Grocery", 40, 50),
            ("Milk", "Dairy", 25, 100),
            ("Rice", "Grains", 60, 30),
            ("Biscuits", "Snacks", 10, 20),
            ("Tea", "Beverages", 120, 15)
        ]
        for name, category, price, stock in products:
            cursor.execute("INSERT INTO Products (name, category, price, stock) VALUES (?, ?, ?, ?)", (name, category, price, stock))
        conn.commit()
    
    conn.close()

def capture_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your order...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            return "Could not understand audio. Please try again."
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}"
        

DATABASE_PATH = "kirana_store.db"

def parse_order(command):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    items = []
    command = command.lower()

    # Retrieve all product names from the database
    cursor.execute("SELECT name FROM Products")
    products = cursor.fetchall()  
    product_names = [product[0].lower() for product in products]

    stock_exists = False
    count=0

    splitted_command = command.split()

    quantity_list = []

    try:
        quantity=-1
        for word in splitted_command:
            try:
                digit = w2n.word_to_num(word)
            except:
                digit=None
            if digit and isinstance(w2n.word_to_num(word) , int):
                quantity=w2n.word_to_num(word)
                quantity_list.append(w2n.word_to_num(word))

        if quantity==-1:
            raise Exception
    except:
        return items, stock_exists, len(product_names), count
    
    i=0
    for product_name in product_names:
        if product_name in command:
            cursor.execute("SELECT name, stock FROM Products WHERE LOWER(name) = ?", (product_name,))
            product = cursor.fetchone()
            if product:
                item_name, stock = product
                if stock >= quantity: 
                    items.append((item_name, quantity_list[i])) 
                    stock_exists = True
                else:
                    print(f"Not enough stock for {item_name}. Requested: {quantity}, Available: {stock}")

                i+=1

        count+=1

    conn.commit()
    conn.close()
    return items, stock_exists, len(product_names), count


def process_order(customer_name, items):
    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()
    unavailable_items = []
    total_items = []

    for item_name, quantity in items:
        cursor.execute("SELECT stock FROM Products WHERE name = ?", (item_name,))
        result = cursor.fetchone()
        if result and result[0] >= quantity:
            cursor.execute("UPDATE Products SET stock = stock - ? WHERE name = ?", (quantity, item_name))
            total_items.append(f"{quantity} x {item_name}")
            conn.commit()
        else:
            unavailable_items.append(item_name)

    delivery_time = time.strftime("%I:%M %p", time.localtime(time.time() + random.randint(300, 1200)))
    order_status = "Processing"

    cursor.execute("INSERT INTO Orders (customer_name, items, delivery_time, status) VALUES (?, ?, ?, ?)",
                   (customer_name, ", ".join(total_items), delivery_time, order_status))
    conn.commit()
    conn.close()

    return total_items, unavailable_items, delivery_time

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    customer_name = data.get("customer_name")
    command = data.get("voice_command")

    if not customer_name or not command:
        return jsonify({"error": "Missing customer_name or voice_command"}), 400

    items, stock_exists, total_products, loop_count = parse_order(command)

    if not items and total_products==loop_count:
        return jsonify({"error": "No recognizable items in voice command."}), 400
    
    if not items and not stock_exists:
        return jsonify({"error": "Quantity Insufficient."}), 400

    total_items, unavailable_items, delivery_time = process_order(customer_name, items)

    ordered_item_names = [item[0] for item in items]
    recommendations = recommendation.recommend_products(ordered_item_names)

    unique_product_names = list({rec.split('x').pop().strip() for rec in recommendations if rec.strip()})


    response = {
        "customer_name": customer_name,
        "order": total_items,
        "unavailable_items": unavailable_items,
        "recommended_products": unique_product_names,
        "estimated_delivery_time": delivery_time,
        "status": "Order placed successfully"
    }

    print(response)
    return jsonify(response), 200


@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    item_name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    stock = data.get("stock")

    if not item_name or not category or price is None or stock is None:
        return jsonify({"error": "Invalid input. 'name', 'category', 'price', and 'stock' are required."}), 400

    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM Products WHERE LOWER(name) = LOWER(?)", (item_name,))


    cursor.execute("INSERT INTO Products (name, category, price, stock) VALUES (?, ?, ?, ?)", (item_name, category, price, stock))

    conn.commit()
    conn.close()

    return jsonify({"message": f"Item '{item_name}' updated successfully."}), 200

@app.route('/update_item', methods=['POST'])
def update_item():
    data = request.get_json()
    product_id = data.get("id")
    new_price = data.get("price")
    new_stock = data.get("stock")

    if product_id is None or new_price is None or new_stock is None:
        return jsonify({"error": "Invalid input. 'id', 'price', and 'stock' are required."}), 400

    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE Products SET price = ?, stock = ? WHERE id = ?", (new_price, new_stock, product_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item updated successfully."}), 200


@app.route('/delete_item', methods=['POST'])
def delete_item():
    try:
        data = request.get_json()
        product_id = data.get('id')

        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        existing_item = fetch_query("SELECT * FROM Products WHERE id = ?", (product_id,))
        print(existing_item)
        if not existing_item:
            return jsonify({"error": "Item not found"}), 404

        execute_query("DELETE FROM Products WHERE id = ?", (product_id,))

        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/orders', methods=['GET'])
def list_orders():
    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()

    current_time = time.strftime("%I:%M %p", time.localtime())

    cursor.execute("SELECT id, customer_name, items, delivery_time, status FROM Orders")
    orders = cursor.fetchall()  

    for order in orders:
        order_id, customer_name, items, delivery_time, status = order
        if delivery_time <= current_time and status != 'Delivered':
            cursor.execute("UPDATE Orders SET status = 'Delivered' WHERE id = ?", (order_id,))
    
    conn.commit()  


    cursor.execute("SELECT id, customer_name, items, delivery_time, status FROM Orders")
    orders = cursor.fetchall()

    conn.close()

    orders_list = []
    for order in orders:
        orders_list.append({
            "id": order[0],
            "customer_name": order[1],
            "items": order[2],
            "delivery_time": order[3],
            "status": order[4]
        })

    return jsonify(orders_list), 200


@app.route('/get_products', methods=['GET'])
def get_products():
    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, stock, price FROM Products")
    products = cursor.fetchall()

    conn.close()

    product_list = [{"name": product[0], "stock": product[1], "price": product[2]} for product in products]
    return jsonify(product_list), 200



@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/orders_page', methods=['GET'])
def orders_page():

    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, customer_name, items, delivery_time, status FROM Orders")
    orders = cursor.fetchall()

    formatted_orders = []
    for order in orders:
        formatted_orders.append({
            'id': order[0],
            'customer_name': order[1],
            'items': order[2],
            'delivery_time': order[3],
            'status': order[4]
        })

    conn.close()

    return render_template('orders.html', orders=formatted_orders)


@app.route('/inventory', methods=['GET'])
def show_inventory():
    conn = sqlite3.connect("kirana_store.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, category, price, stock FROM Products")
    products = cursor.fetchall() 

    conn.close()
    return render_template("inventory.html", products=products)

if __name__ == '__main__':
    init_db()
    populate_dummy_data()
    app.run(debug=True)
