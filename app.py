from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeTimedSerializer
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "secret123"  # Required for flash messages

# Email config (replace with your Gmail details)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'deepashreengd@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'gvhw viuj mwyo gjip'  # Replace with Gmail app password

# OAuth config (replace with your Google credentials)
app.config['GOOGLE_CLIENT_ID'] = 'YOUR_CLIENT_ID'
app.config['GOOGLE_CLIENT_SECRET'] = 'YOUR_CLIENT_SECRET'

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# Mail and OAuth
mail = Mail(app)
oauth = OAuth(app)
s = URLSafeTimedSerializer(app.secret_key)

class User(UserMixin):
    def __init__(self, user_id, email, role):
        self.id = user_id
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['user_id'], user['email'], user['role'])
    return None

# Google OAuth
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'email profile'}
)

# Database helper
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------- Authentication --------------------
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Invalid email format!", "danger")
        return redirect(url_for("home"))

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        user_obj = User(user['user_id'], user['email'], user['role'])
        login_user(user_obj)
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]  # Use username instead of email
        session["role"] = user["role"]
        role = user["role"]
        if role == "Admin":
            return redirect(url_for("admin_dashboard"))
        elif role == "Supplier":
            return redirect(url_for("supplier_dashboard"))
        else:
            return redirect(url_for("user_dashboard"))
    else:
        flash("Invalid email or password!", "danger")
        return redirect(url_for("home"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format!", "danger")
            return redirect(url_for("signup"))

        # Password validation
        special_chars = r'[!@#$%^&*()_+\-=\[\]{}|;:\'",./<>?]'
        if not (len(password) >= 8 and re.search(special_chars, password)):
            flash("Password must be at least 8 characters long and include at least one special character (e.g., !@#$%^&*).", "danger")
            return redirect(url_for("signup"))

        conn = get_db()
        try:
            # Check if admin already exists
            if role == "Admin":
                existing_admin = conn.execute("SELECT * FROM users WHERE role = 'Admin'").fetchone()
                if existing_admin:
                    flash("An admin already exists. Only one admin allowed.", "danger")
                    return redirect(url_for("signup"))

            hashed_password = generate_password_hash(password)
            conn.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                         (username, email, hashed_password, role))
            conn.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("home"))
        except:
            flash("Email or username already exists!", "danger")
            return redirect(url_for("signup"))
        finally:
            conn.close()

    return render_template("signup.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format!", "danger")
            return redirect(url_for("forgot_password"))
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user:
            try:
                token = s.dumps(email, salt='password-reset')
                msg = Message('Password Reset for Stock Sync', sender=app.config['MAIL_USERNAME'], recipients=[email])
                link = url_for('reset_password', token=token, _external=True)
                msg.body = f'Hello, \n\nClick the following link to reset your password: {link}\n\nIf you did not request this, ignore this email.\n\nThanks, Stock Sync Team'
                mail.send(msg)
                flash("Password reset email sent! Check your inbox.", "success")
            except Exception as e:
                flash("Failed to send email. Please try again later.", "danger")
                print(f"Mail error: {e}")
        else:
            flash("If the email exists, a reset link has been sent.", "info")
        return redirect(url_for("home"))
    return render_template("forgot_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except:
        flash("The reset link is invalid or has expired!", "danger")
        return redirect(url_for("home"))
    if request.method == "POST":
        password = request.form["password"]
        confirm = request.form["confirm_password"]
        if password != confirm:
            flash("Passwords do not match!", "danger")
            return render_template("reset_password.html", token=token)
        if len(password) < 6:
            flash("Password must be at least 6 characters!", "danger")
            return render_template("reset_password.html", token=token)
        hashed = generate_password_hash(password)
        conn = get_db()
        conn.execute("UPDATE users SET password=? WHERE email=?", (hashed, email))
        conn.commit()
        conn.close()
        flash("Password reset successful! Please login.", "success")
        return redirect(url_for("home"))
    return render_template("reset_password.html", token=token)

@app.route("/login/google")
def login_google():
    try:
        if not current_user.is_authenticated:
            return google.authorize_redirect(url_for('auth_google', _external=True))
        return redirect(url_for("user_dashboard"))
    except Exception as e:
        flash("Error during Google login. Please try again.", "danger")
        print(f"Google login error: {e}")
        return redirect(url_for("home"))

@app.route("/auth/google")
def auth_google():
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        email = user_info['email']
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            # Create user with role User
            hashed = generate_password_hash('default123')
            username = user_info.get('name', email.split('@')[0])  # Use name if available, else email prefix
            conn.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", (username, email, hashed, "User"))
            conn.commit()
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        user_obj = User(user['user_id'], user['email'], user['role'])
        login_user(user_obj, remember=True)
        session["user_id"] = user['user_id']
        session["username"] = user['email']
        session["role"] = user['role']
        if user["role"] == "Admin":
            return redirect(url_for("admin_dashboard"))
        elif user["role"] == "Supplier":
            return redirect(url_for("supplier_dashboard"))
        else:
            return redirect(url_for("user_dashboard"))
    except Exception as e:
        flash("Error during Google authentication. Please try again.", "danger")
        print(f"Google auth error: {e}")
        return redirect(url_for("home"))

# -------------------- Dashboards --------------------
@app.route("/admin")
@login_required
def admin_dashboard():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    low_stock_products = conn.execute("SELECT * FROM products WHERE quantity < threshold").fetchall()
    conn.close()
    username = session.get("username", "User")
    if low_stock_products:
        flash(f"Warning: {len(low_stock_products)} product(s) are below the threshold level. Please restock.", "warning")
    return render_template("dashboard.html", role="Admin", username=username, products=products, low_stock_products=low_stock_products)

@app.route("/supplier")
@login_required
def supplier_dashboard():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    username = session.get("username", "User")
    return render_template("supplier_products.html", username=username, products=products)

@app.route("/user")
@login_required
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))
    user_id = session["user_id"]
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    cart_items = conn.execute("""
        SELECT p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ?
    """, (user_id,)).fetchall()
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    # Group products by category
    products_by_category = {}
    for product in products:
        category = product['category']
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)
    conn.close()
    username = session.get("username", "User")
    return render_template("user_dashboard.html", username=username, products_by_category=products_by_category, cart_items=cart_items, total_price=total_price)

@app.route("/cart")
@login_required
def view_cart():
    if "user_id" not in session or session.get("role") != "User":
        flash("Access denied. Only users can access the cart.", "danger")
        return redirect(url_for("home"))
    user_id = session["user_id"]
    conn = get_db()
    cart_items = conn.execute("""
        SELECT p.name, p.price, c.quantity, p.product_id
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ?
    """, (user_id,)).fetchall()
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    conn.close()
    username = session.get("username", "User")
    return render_template("cart.html", username=username, cart_items=cart_items, total_price=total_price)

@app.route("/user/category/<category>")
@login_required
def view_category(category):
    if "user_id" not in session:
        return redirect(url_for("home"))
    user_id = session["user_id"]
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE category = ?", (category,)).fetchall()
    cart_items = conn.execute("""
        SELECT p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ?
    """, (user_id,)).fetchall()
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    conn.close()
    username = session.get("username", "User")
    return render_template("category_products.html", username=username, category=category, products=products, cart_items=cart_items, total_price=total_price)

# -------------------- Products --------------------
@app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        qty = request.form["quantity"]
        price = request.form["price"]
        threshold = request.form["threshold"]

        conn = get_db()
        conn.execute("INSERT INTO products (name, category, quantity, price, threshold) VALUES (?, ?, ?, ?, ?)",
                     (name, category, qty, price, threshold))
        conn.commit()
        conn.close()
        flash("Product added successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("add_product.html")

@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        qty = request.form["quantity"]
        price = request.form["price"]
        threshold = request.form["threshold"]

        conn.execute("""UPDATE products SET name=?, category=?, quantity=?, price=?, threshold=? 
                        WHERE product_id=?""",
                     (name, category, qty, price, threshold, product_id))
        conn.commit()
        conn.close()
        flash("Product updated successfully!", "success")
        return redirect(url_for("view_products"))
    conn.close()
    return render_template("edit_product.html", product=product)

@app.route("/delete_product/<int:product_id>")
@login_required
def delete_product(product_id):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()
    flash("Product deleted successfully!", "success")
    return redirect(url_for("view_products"))

@app.route("/view_products")
@login_required
def view_products():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    role = session.get("role")
    username = session.get("username")
    return render_template("view_products.html", products=products, role=role, username=username)

@app.route("/manage_users")
@login_required
def manage_users():
    if session.get("role") != "Admin":
        flash("Access denied. Only admins can manage users.", "danger")
        return redirect(url_for("admin_dashboard"))
    conn = get_db()
    users = conn.execute("SELECT user_id, username, email, role FROM users").fetchall()
    conn.close()
    username = session.get("username", "User")
    return render_template("manage_users.html", users=users, username=username)

@app.route("/report")
@login_required
def report():
    conn = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    # Get sales data for the sales chart
    sales_data = conn.execute("""
        SELECT strftime('%Y-%m-%d', sale_date) as date, SUM(total_price) as revenue, SUM(quantity) as units_sold
        FROM sales
        GROUP BY strftime('%Y-%m-%d', sale_date)
        ORDER BY date DESC
        LIMIT 30
    """).fetchall()
    conn.close()
    role = session.get("role")
    username = session.get("username")
    # Convert Row objects to dictionaries for JSON serialization
    products_list = [dict(product) for product in products]
    sales_list = [dict(sale) for sale in sales_data]
    return render_template("report.html", products=products_list, sales=sales_list, role=role, username=username)

@app.route("/search")
@login_required
def search():
    q = request.args.get("q", "")
    conn = get_db()
    products = conn.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + q + '%',)).fetchall()
    conn.close()
    username = session.get("username", "User")
    user_id = session.get("user_id")
    cart_items = []
    if user_id:
        conn = get_db()
        cart_items = conn.execute("""
            SELECT p.name, p.price, c.quantity
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = ?
        """, (user_id,)).fetchall()
        conn.close()
    return render_template("search.html", products=products, username=username, cart_items=cart_items)

@app.route("/profile")
@login_required
def profile():
    username = session.get("username", "User")
    return render_template("profile.html", username=username)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    username = session.get("username", "User")
    if request.method == "POST":
        new_username = request.form["username"]
        new_password = request.form["password"]
        user_id = session["user_id"]
        conn = get_db()
        if new_password:
            # Password validation
            special_chars = r'[!@#$%^&*()_+\-=\[\]{}|;:\'",./<>?]'
            if not (len(new_password) >= 8 and re.search(special_chars, new_password)):
                flash("Password must be at least 8 characters long and include at least one special character (e.g., !@#$%^&*).", "danger")
                return redirect(url_for("settings"))
            hashed_password = generate_password_hash(new_password)
            conn.execute("UPDATE users SET username=?, password=? WHERE user_id=?", (new_username, hashed_password, user_id))
        else:
            conn.execute("UPDATE users SET username=? WHERE user_id=?", (new_username, user_id))
        conn.commit()
        conn.close()
        session["username"] = new_username
        flash("Settings updated successfully!", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html", username=username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/supply_stock/<int:product_id>", methods=["GET", "POST"])
@login_required
def supply_stock(product_id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()
    if request.method == "POST":
        supply_qty = int(request.form["supply_quantity"])
        new_qty = product["quantity"] + supply_qty
        conn.execute("UPDATE products SET quantity=? WHERE product_id=?", (new_qty, product_id))
        conn.commit()
        conn.close()
        flash("Stock supplied successfully!", "success")
        return redirect(url_for("supplier_dashboard"))
    conn.close()
    return render_template("supply_stock.html", product=product)

# -------------------- Cart --------------------
@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    if "user_id" not in session or session.get("role") != "User":
        flash("Access denied. Only users can add items to cart.", "danger")
        return redirect(url_for("home"))
    user_id = session["user_id"]
    quantity = int(request.form["quantity"])
    conn = get_db()
    # Check if already in cart
    existing = conn.execute("SELECT * FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id)).fetchone()
    if existing:
        new_qty = existing["quantity"] + quantity
        conn.execute("UPDATE cart SET quantity = ? WHERE cart_id = ?", (new_qty, existing["cart_id"]))
    else:
        conn.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (user_id, product_id, quantity))
    conn.commit()
    conn.close()
    flash("Product added to cart!", "success")
    return redirect(url_for("user_dashboard"))

@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    if "user_id" not in session or session.get("role") != "User":
        flash("Access denied. Only users can checkout.", "danger")
        return redirect(url_for("home"))
    user_id = session["user_id"]
    payment_method = request.form.get("payment_method", "cash_on_delivery")
    conn = get_db()
    cart_items = conn.execute("""
        SELECT c.cart_id, c.product_id, c.quantity, p.quantity as available, p.price
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ?
    """, (user_id,)).fetchall()
    for item in cart_items:
        if item["quantity"] > item["available"]:
            flash(f"Not enough stock for {item['product_id']}", "danger")
            return redirect(url_for("view_cart"))
        new_qty = item["available"] - item["quantity"]
        conn.execute("UPDATE products SET quantity = ? WHERE product_id = ?", (new_qty, item["product_id"]))
        # Record sale
        total_price = item["price"] * item["quantity"]
        conn.execute("INSERT INTO sales (user_id, product_id, quantity, total_price, payment_method) VALUES (?, ?, ?, ?, ?)",
                     (user_id, item["product_id"], item["quantity"], total_price, payment_method))
    # Clear cart
    conn.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash(f"Purchase successful! Payment method: {payment_method.replace('_', ' ').title()}", "success")
    return redirect(url_for("user_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
