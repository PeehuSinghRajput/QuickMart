# QuickMart
QuickMart is a user-friendly, efficient inventory and order management system designed for small businesses. With real-time updates and a responsive interface, it allows seamless product tracking, order processing, and stock management, ensuring smooth operations and better customer satisfaction—all at your fingertips!

QuickMart is a simple web-based system built using Flask for managing inventory and customer orders. The system allows an admin to add, update, and delete products in the inventory, as well as view customer orders with detailed information such as customer name, ordered items, delivery time, and order status.

The frontend is developed using HTML, CSS (with Bootstrap for responsiveness), and JavaScript (with jQuery for AJAX functionality), ensuring a smooth and interactive user experience.

---

## Features

- **Inventory Management**:
  - Add new products to the inventory.
  - Update product details such as price and stock.
  - Delete products from the inventory.
  
- **Order Management**:
  - View all placed orders with details including customer name, items ordered, delivery time, and order status.
  - Real-time updates of the order status.

- **Responsive Design**:
  - Fully responsive user interface with mobile-friendly design.

- **AJAX Functionality**:
  - Seamless updates without the need for page reloads.

---

## Technologies Used

- **Backend**: Flask
- **Frontend**: HTML, CSS (Bootstrap), JavaScript (jQuery)
- **Database**: SQLite (or any other suitable database, depending on future extension)
- **AJAX** for dynamic content updating
- **Bootstrap** for responsive layout and design

---

## Setup Instructions

### Prerequisites

Make sure you have Python 3.x installed on your system.

### Installation Steps

1. Clone this repository:
    - using git clone command 
    - cd QuickMart

2. Create a virtual environment:
    - python3 -m venv venv
    - source venv/bin/activate  # For Linux/Mac
    - venv\Scripts\activate     # For Windows

3. Install the required dependencies:
    pip install -r requirements.txt

4. Run the Flask application:
    python index.py

5. Open your browser and visit http://localhost:5000 to access the application.

## Endpoints
1. / : Displays the main Dashboard for QuickMart where user can give order using voice command and get product recommendation on category basis and estimation of delivery time for their ordered product
2. /inventory : Endpoint to show inventory dashboard where user can add , update, delete product items and manage their stocks and price
3. /orders_page : Endpoint to show the list of orders placed with their user details and the quantity and items details in the list format with their tracking details.

