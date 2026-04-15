# 🥦 Online Vegetable Shop (OVS)

A web application for browsing and purchasing fresh vegetables online with admin management capabilities.

---

## 🚀 Features

### User Features
- **Authentication**: Secure register/login system
- **Browse Products**: View and search vegetables
- **Shopping Cart**: Add, update, and remove items
- **Checkout**: Place orders with stock validation
- **Order History**: View past orders and status

### Admin Features
- **Product Management**: Add, edit, delete products
- **Stock Management**: Real-time inventory tracking
- **Order Management**: View and update order statuses

---

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS

---

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+

---

## ⚙️ Installation

### 1. Install PostgreSQL

Download and install from: https://www.postgresql.org/download/

### 2. Create Database

```sql
CREATE DATABASE online_vegetable_shop;
```

### 3. Clone/Download Project

Navigate to the project directory:

```bash
cd backend
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Database Connection

Update the database URI in `app.py` (line 11-13):

```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://postgres:your_password@localhost:5432/online_vegetable_shop'
)
```

Or set environment variable:

```bash
set DATABASE_URL=postgresql://postgres:your_password@localhost:5432/online_vegetable_shop
```

### 6. Run the Application

```bash
python app.py
```

The app will:
- Create all database tables automatically
- Create a default admin user (username: `admin`, password: `admin123`)
- Add sample vegetable products

Visit: **http://localhost:5000**

---

## 👤 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change this password in production!**

---

## 📁 Project Structure

```
OVS/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── static/
│   └── css/
│       └── style.css          # Stylesheet
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Home/Product listing
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── cart.html              # Shopping cart
    ├── checkout.html          # Checkout page
    ├── profile.html           # User orders
    └── admin/
        ├── dashboard.html     # Admin dashboard
        └── product_form.html  # Add/Edit product
```

---

## 🗄️ Database Schema

### Users
- id, username, email, password_hash, role, created_at

### Products
- id, name, description, price, stock, image_url, is_available, created_at

### Cart
- id, user_id, product_id, quantity, added_at

### Orders
- id, user_id, total_amount, status, order_date

### Order_Items
- id, order_id, product_id, quantity, price

---

## 🎯 Usage

1. **Register** a new account or **login** with existing credentials
2. **Browse** vegetables on the home page
3. **Search** for specific vegetables
4. **Add items** to cart with desired quantity
5. **Checkout** and place your order
6. **View orders** in your profile
7. **Admin users** can manage products and orders via `/admin`

---

## 🔒 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Stock validation before order placement
- Admin-only route protection

---

## 🚀 Future Enhancements

- Online payment integration (Stripe, Razorpay)
- Delivery tracking system
- Email notifications
- Product categories and filters
- User reviews and ratings
- Mobile app

---

## 📝 License

MIT License

---

## 🆘 Support

For issues or questions, please create an issue in the repository.
