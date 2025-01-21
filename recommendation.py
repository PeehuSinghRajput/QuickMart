import sqlite3
from collections import Counter
from itertools import combinations

DATABASE_PATH = "kirana_store.db"

def get_past_orders():
    """Fetch past orders from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT items FROM Orders")
    orders = cursor.fetchall()  

    conn.close()

    past_orders = []
    for order in orders:
        items = order[0].split(", ")
        past_orders.append([item.strip().lower() for item in items])

    return past_orders

def get_all_products():
    """Fetch all products and their categories from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, category FROM Products")
    products = cursor.fetchall()  

    conn.close()

    return {product[1].lower(): (product[0], product[1], product[2]) for product in products}

def generate_recommendations(target_items, past_orders, all_products, top_n=5):
    """Generate product recommendations based on past orders and item categories.

    Args:
        target_items (list): List of items the customer is ordering.
        past_orders (list): List of past orders.
        all_products (dict): Dictionary of products indexed by category.
        top_n (int): Number of recommendations to return.

    Returns:
        list: Recommended products.
    """
    ordered_categories = set()
    for item in target_items:
        item = item.strip().lower()
        product = all_products.get(item)
        if product:
            ordered_categories.add(product[2].lower())

    if not ordered_categories:
        return []

    category_counts = Counter()
    for order in past_orders:
        for item in order:
            item = item.strip().lower()
            product = all_products.get(item)
            if product:
                category_counts[product[2].lower()] += 1

    recommendation_scores = {}
    for category in ordered_categories:
        for product_name, product_data in all_products.items():
            if product_data[2].lower() == category and product_name not in target_items:
                recommendation_scores[product_name] = recommendation_scores.get(product_name, 0) + category_counts[category]

    sorted_recommendations = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
    return [product for product, score in sorted_recommendations[:top_n]]

def recommend_products(customer_order):
    """Main function to recommend products for a customer order.

    Args:
        customer_order (list): List of items the customer wants to order.

    Returns:
        list: Recommended products.
    """
    past_orders = get_past_orders()
    all_products = get_all_products()  
    recommendations = generate_recommendations(customer_order, past_orders, all_products)
    return recommendations

if __name__ == "__main__":
    customer_order = ["milk", "sugar"]
    recommendations = recommend_products(customer_order)
    print("Recommended Products:", recommendations)
