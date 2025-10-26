# Stock Sys - Inventory Management System

## Project Overview

Stock Sys is a comprehensive web-based inventory management system built with Flask. It allows businesses to manage products, track stock levels, handle user roles (Admin, Supplier, User), and facilitate e-commerce functionality including shopping carts and sales reporting.

## Features

### User Management
- **Role-based Access Control**: Admin, Supplier, and User roles with different permissions
- **Authentication**: Email/password login with secure password hashing
- **OAuth Integration**: Google OAuth for easy login
- **Password Reset**: Email-based password recovery system
- **User Profiles**: Profile management and settings

### Product Management
- **CRUD Operations**: Create, read, update, and delete products
- **Categorization**: Products organized by categories (Electronics, Clothing, Home & Garden, Books, Sports & Outdoors)
- **Stock Tracking**: Real-time inventory monitoring with threshold alerts
- **Search Functionality**: Product search across the inventory

### E-commerce Features
- **Shopping Cart**: Add/remove products, quantity management
- **Checkout Process**: Multiple payment methods (Cash on Delivery, etc.)
- **Sales Tracking**: Record and analyze sales data
- **Reports**: Dashboard with sales charts and inventory reports

### Supplier Features
- **Stock Supply**: Suppliers can add stock to existing products
- **Product Oversight**: View all products and manage inventory levels

### Admin Features
- **User Management**: View and manage all users
- **Product Oversight**: Full control over product catalog
- **Low Stock Alerts**: Automatic warnings for products below threshold
- **System Reports**: Comprehensive analytics and reporting

## Tech Stack

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLite 3
- **Authentication**: Flask-Login 0.6.3
- **Email**: Flask-Mail 0.9.1
- **OAuth**: Authlib 1.2.1
- **Security**: Werkzeug 2.3.7 (password hashing), itsdangerous 2.1.2 (token generation)
- **Environment**: python-dotenv 1.0.0

### Frontend
- **Templates**: Jinja2 (Flask default)
- **Styling**: Custom CSS
- **JavaScript**: Vanilla JS for client-side interactions
- **Responsive Design**: Bootstrap-compatible layouts

### Deployment
- **Platform**: Heroku
- **Python Version**: 3.9.7
- **Process Management**: Procfile for web process

## Installation

### Prerequisites
- Python 3.9.7
- pip (Python package manager)

### Setup Steps

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd /path/to/stock-sync
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```

5. **Configure environment variables**:
   Create a `.env` file in the root directory with:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

6. **Configure email settings** in `app.py`:
   - Update `MAIL_USERNAME` and `MAIL_PASSWORD` with your Gmail credentials
   - Use an app password for Gmail authentication

## Usage

### Running the Application

1. **Development mode**:
   ```bash
   python app.py
   ```
   The application will run on `http://localhost:5000`

2. **Production deployment** (Heroku):
   - Ensure `Procfile` and `runtime.txt` are present
   - Deploy to Heroku using their CLI or dashboard

### Default Users

The system comes with pre-configured default users:

- **Admin**: email: `admin@stock.com`, password: `admin123`
- **Supplier**: email: `supplier@stock.com`, password: `supplier123`
- **User**: email: `user@stock.com`, password: `user123`

### Accessing Different Dashboards

- **Admin Dashboard**: `/admin` - Full system management
- **Supplier Dashboard**: `/supplier` - Stock management
- **User Dashboard**: `/user` - Shopping interface

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
```

### Products Table
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    threshold INTEGER NOT NULL
);
```

### Cart Table
```sql
CREATE TABLE cart (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
```

### Sales Table
```sql
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_price REAL NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
```

## API Endpoints

### Authentication
- `GET /` - Login page
- `POST /login` - User login
- `GET/POST /signup` - User registration
- `GET/POST /forgot_password` - Password reset request
- `GET/POST /reset_password/<token>` - Password reset
- `GET /login/google` - Google OAuth login
- `GET /auth/google` - Google OAuth callback
- `GET /logout` - User logout

### Dashboards
- `GET /admin` - Admin dashboard
- `GET /supplier` - Supplier dashboard
- `GET /user` - User dashboard

### Product Management
- `GET/POST /add_product` - Add new product
- `GET/POST /edit_product/<product_id>` - Edit product
- `GET /delete_product/<product_id>` - Delete product
- `GET /view_products` - View all products
- `GET /search` - Search products

### Cart & Checkout
- `GET /cart` - View shopping cart
- `POST /add_to_cart/<product_id>` - Add item to cart
- `POST /checkout` - Process purchase

### Supplier Functions
- `GET/POST /supply_stock/<product_id>` - Supply stock

### Admin Functions
- `GET /manage_users` - User management
- `GET /report` - System reports

### User Functions
- `GET /profile` - User profile
- `GET/POST /settings` - User settings
- `GET /user/category/<category>` - Products by category

## Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Management**: Flask-Login for secure session handling
- **CSRF Protection**: Built-in Flask-WTF protection
- **Input Validation**: Server-side validation for all forms
- **Email Verification**: Token-based password reset
- **Role-based Access**: Strict permission checks for sensitive operations

## Deployment

### Heroku Deployment

1. **Install Heroku CLI**
2. **Login to Heroku**:
   ```bash
   heroku login
   ```
3. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```
4. **Set environment variables**:
   ```bash
   heroku config:set GOOGLE_CLIENT_ID=your_client_id
   heroku config:set GOOGLE_CLIENT_SECRET=your_client_secret
   ```
5. **Deploy**:
   ```bash
   git push heroku main
   ```

### Local Production Run

```bash
export PORT=8000
python app.py
```

## Configuration

### Email Configuration
Update the following in `app.py`:
```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

### OAuth Configuration
Set environment variables:
```bash
export GOOGLE_CLIENT_ID=your_client_id
export GOOGLE_CLIENT_SECRET=your_client_secret
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please contact the development team or create an issue in the repository.
