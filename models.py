import sqlite3

DATABASE_PATH = "kirana_store.db"


class Product:
    def __init__(self, id, name, stock, category, price):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock

    @staticmethod
    def create_table():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        )''')
        conn.commit()
        conn.close()

    @staticmethod
    def add_product(name, stock):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Products (name, stock) VALUES (?, ?)", (name, stock))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_products():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        conn.close()
        return [Product(id, name, stock) for id, name, stock in products]

    @staticmethod
    def get_product_by_name(name):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products WHERE name = ?", (name,))
        product = cursor.fetchone()
        conn.close()
        if product:
            return Product(*product)
        return None

class Order:
    def __init__(self, id, customer_name, items, delivery_time, status):
        self.id = id
        self.customer_name = customer_name
        self.items = items
        self.delivery_time = delivery_time
        self.status = status

    @staticmethod
    def create_table():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            items TEXT NOT NULL,
            delivery_time TEXT NOT NULL,
            status TEXT NOT NULL
        )''')
        conn.commit()
        conn.close()

    @staticmethod
    def add_order(customer_name, items, delivery_time, status):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Orders (customer_name, items, delivery_time, status) VALUES (?, ?, ?, ?)",
                       (customer_name, items, delivery_time, status))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_orders():
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Orders")
        orders = cursor.fetchall()
        conn.close()
        return [Order(id, customer_name, items, delivery_time, status) for id, customer_name, items, delivery_time, status in orders]

    @staticmethod
    def update_order_status(order_id, new_status):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE Orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        conn.close()
