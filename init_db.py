import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Users table (for Admin, Supplier, User)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    threshold INTEGER NOT NULL
)
""")

# Cart table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
)
""")

# Sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
)
""")

# Insert default users
cursor.executemany("""
INSERT OR IGNORE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)
""", [
    ("admin", "admin@stock.com", generate_password_hash("admin123"), "Admin"),
    ("supplier", "supplier@stock.com", generate_password_hash("supplier123"), "Supplier"),
    ("user", "user@stock.com", generate_password_hash("user123"), "User")
])

# Insert sample products in different categories
cursor.executemany("""
INSERT OR IGNORE INTO products (name, category, quantity, price, threshold) VALUES (?, ?, ?, ?, ?)
""", [
    # Electronics
    ("Laptop", "Electronics", 50, 999.99, 10),
    ("Smartphone", "Electronics", 100, 699.99, 20),
    ("Headphones", "Electronics", 75, 149.99, 15),
    ("Tablet", "Electronics", 30, 399.99, 5),
    ("Smart Watch", "Electronics", 40, 299.99, 8),

    # Clothing
    ("T-Shirt", "Clothing", 200, 19.99, 50),
    ("Jeans", "Clothing", 150, 49.99, 30),
    ("Jacket", "Clothing", 80, 89.99, 15),
    ("Sneakers", "Clothing", 120, 79.99, 25),
    ("Hat", "Clothing", 90, 14.99, 20),

    # Home & Garden
    ("Chair", "Home & Garden", 60, 149.99, 10),
    ("Table", "Home & Garden", 25, 299.99, 5),
    ("Lamp", "Home & Garden", 45, 39.99, 10),
    ("Garden Hose", "Home & Garden", 70, 24.99, 15),
    ("Pillow", "Home & Garden", 100, 29.99, 20),

    # Books
    ("Fiction Novel", "Books", 80, 12.99, 20),
    ("Cookbook", "Books", 60, 24.99, 10),
    ("Textbook", "Books", 40, 89.99, 5),
    ("Children's Book", "Books", 120, 9.99, 25),
    ("Biography", "Books", 50, 19.99, 10),

    # Sports & Outdoors
    ("Basketball", "Sports & Outdoors", 35, 29.99, 5),
    ("Tennis Racket", "Sports & Outdoors", 25, 79.99, 5),
    ("Yoga Mat", "Sports & Outdoors", 55, 39.99, 10),
    ("Dumbbells", "Sports & Outdoors", 40, 49.99, 8),
    ("Camping Tent", "Sports & Outdoors", 20, 199.99, 3)
])

conn.commit()
conn.close()
print("Database initialized successfully!")

