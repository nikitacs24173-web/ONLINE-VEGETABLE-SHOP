from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend'),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ovs.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    prices = db.relationship('ProductPrice', backref='product', lazy='joined', cascade='all, delete-orphan', order_by='ProductPrice.price')
    cart_items = db.relationship('Cart', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class ProductPrice(db.Model):
    __tablename__ = 'product_prices'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.String(20), nullable=False)  # '250g', '500g', '1kg'
    price = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (db.UniqueConstraint('product_id', 'quantity', name='_product_quantity_uc'),)

class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('product_prices.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    price_option = db.relationship('ProductPrice', backref='cart_items', lazy='joined')

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', 'price_id', name='_user_product_price_uc'),)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payment_method = db.Column(db.String(50), default='upi')
    utr_number = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='completed')  # pending, completed, failed
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='payment')
    user = db.relationship('User', backref='payments')

# ==================== AUTH DECORATORS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admin only.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
@login_required
def shop():
    search_query = request.args.get('search', '')
    if search_query:
        products = Product.query.filter(
            Product.name.ilike(f'%{search_query}%'),
            Product.is_available == True
        ).all()
    else:
        products = Product.query.filter_by(is_available=True).all()
    return render_template('shop.html', products=products, search_query=search_query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['role'] = user.role
            
            # Redirect admin to dashboard
            if user.role == 'admin':
                flash(f'Welcome back, Admin {user.username}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash(f'Welcome back, {user.username}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.order_date.desc()).all()
    return render_template('profile.html', orders=orders)

# ==================== CART ROUTES ====================

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    total = sum(item.price_option.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    price_id = int(request.form.get('price_id', 1))

    product = Product.query.get_or_404(product_id)
    price_option = ProductPrice.query.get_or_404(price_id)

    if product.stock < quantity:
        flash(f'Only {product.stock} items available in stock!', 'warning')
        return redirect(url_for('shop'))

    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id, price_id=price_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=session['user_id'], product_id=product_id, price_id=price_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} ({price_option.quantity}) added to cart!', 'success')
    return redirect(url_for('shop'))

@app.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('cart'))
    
    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated!', 'success')
    else:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'info')
    
    return redirect(url_for('cart'))

# ==================== ORDER ROUTES ====================

@app.route('/checkout')
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    total = sum(item.price_option.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/payment/initiate', methods=['POST'])
@login_required
def initiate_payment():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    # Validate stock
    for item in cart_items:
        if item.product.stock < item.quantity:
            flash(f'Insufficient stock for {item.product.name}!', 'error')
            return redirect(url_for('cart'))

    total = sum(item.price_option.price * item.quantity for item in cart_items)
    return render_template('payment.html', cart_items=cart_items, total=total)

@app.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    data = request.get_json()
    utr_number = data.get('utr')
    amount = data.get('amount')

    if not utr_number or not amount:
        return jsonify({'success': False, 'message': 'Invalid payment details'}), 400

    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    # Create order
    total = sum(item.price_option.price * item.quantity for item in cart_items)
    order = Order(user_id=session['user_id'], total_amount=total, status='confirmed')
    db.session.add(order)
    db.session.flush()

    # Create order items and update stock
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price_option.price
        )
        db.session.add(order_item)
        item.product.stock -= item.quantity
        db.session.delete(item)

    # Create payment record
    payment = Payment(
        order_id=order.id,
        user_id=session['user_id'],
        payment_method='upi',
        utr_number=utr_number,
        amount=total,
        status='completed'
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({'success': True, 'order_id': order.id})

@app.route('/payment/success/<int:order_id>')
@login_required
def payment_success(order_id):
    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    if order.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    return render_template('payment_success.html', order=order, payment=payment)

@app.route('/payment/invoice/<int:order_id>')
@login_required
def download_invoice(order_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    from io import BytesIO
    
    order = Order.query.get_or_404(order_id)
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    if order.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    # Create PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Online Vegetable Shop")
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 75, "Invoice")
    
    # Order details
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 110, f"Order ID: #{order.id}")
    c.drawString(300, height - 110, f"Date: {order.order_date.strftime('%d-%m-%Y %H:%M')}")
    c.drawString(50, height - 130, f"Customer: {order.user.username}")
    c.drawString(300, height - 130, f"Email: {order.user.email}")
    
    # Items table
    data = [['Product', 'Quantity', 'Price', 'Subtotal']]
    for item in order.items:
        data.append([
            item.product.name,
            str(item.quantity),
            f"Rs.{item.price:.2f}",
            f"Rs.{item.price * item.quantity:.2f}"
        ])
    data.append(['', '', 'Total', f"Rs.{order.total_amount:.2f}"])
    
    table = Table(data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 320)
    
    # Payment details
    y_pos = height - 360
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_pos, "Payment Details")
    c.setFont("Helvetica", 11)
    y_pos -= 25
    c.drawString(50, y_pos, f"Payment Method: UPI")
    y_pos -= 20
    c.drawString(50, y_pos, f"UPI ID: ovg@shop123")
    y_pos -= 20
    if payment:
        c.drawString(50, y_pos, f"Transaction ID: {payment.utr_number}")
        y_pos -= 20
    c.drawString(50, y_pos, f"Status: Completed")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Thank you for shopping with us!")
    c.drawString(50, 35, "This is a computer-generated invoice.")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    from flask import send_file
    return send_file(buffer, as_attachment=True, download_name=f'invoice_{order.id}.pdf', mimetype='application/pdf')

@app.route('/order/place', methods=['POST'])
@login_required
def place_order():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()

    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    # Validate stock
    for item in cart_items:
        if item.product.stock < item.quantity:
            flash(f'Insufficient stock for {item.product.name}!', 'error')
            return redirect(url_for('cart'))

    # Create order
    total = sum(item.price_option.price * item.quantity for item in cart_items)
    order = Order(user_id=session['user_id'], total_amount=total)
    db.session.add(order)
    db.session.flush()

    # Create order items and update stock
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price_option.price
        )
        db.session.add(order_item)
        item.product.stock -= item.quantity
        db.session.delete(item)

    db.session.commit()
    flash(f'Order placed successfully! Order #{order.id}', 'success')
    return redirect(url_for('profile'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    products = Product.query.all()
    orders = Order.query.order_by(Order.order_date.desc()).all()
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    users = User.query.all()
    return render_template('admin/dashboard.html', products=products, orders=orders, payments=payments, users=users)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            stock=int(request.form.get('stock')),
            image_url='/static/images/tomato.svg',  # Default image
            is_available=request.form.get('is_available') == 'on'
        )
        db.session.add(product)
        db.session.flush()

        # Add price options for all 7 quantities
        prices = {
            '250g': request.form.get('price_250g'),
            '500g': request.form.get('price_500g'),
            '1kg': request.form.get('price_1kg'),
            '1.25kg': request.form.get('price_1_25kg'),
            '1.5kg': request.form.get('price_1_5kg'),
            '1.75kg': request.form.get('price_1_75kg'),
            '2kg': request.form.get('price_2kg')
        }

        for quantity, price in prices.items():
            if price:
                db.session.add(ProductPrice(product_id=product.id, quantity=quantity, price=float(price)))

        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html', product=None)

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.stock = int(request.form.get('stock'))
        product.is_available = request.form.get('is_available') == 'on'

        # Update prices for all 7 quantities
        prices = {
            '250g': request.form.get('price_250g'),
            '500g': request.form.get('price_500g'),
            '1kg': request.form.get('price_1kg'),
            '1.25kg': request.form.get('price_1_25kg'),
            '1.5kg': request.form.get('price_1_5kg'),
            '1.75kg': request.form.get('price_1_75kg'),
            '2kg': request.form.get('price_2kg')
        }

        for price_option in product.prices:
            if price_option.quantity in prices and prices[price_option.quantity]:
                price_option.price = float(prices[price_option.quantity])

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html', product=product)

@app.route('/admin/product/delete/<int:product_id>')
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order_id} status updated to {new_status}!', 'success')
    
    return redirect(url_for('admin_dashboard'))

# ==================== INITIALIZE DB ====================

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@ovs.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin/admin123')
        
        # Add sample products if none exist
        if Product.query.count() == 0:
            sample_products = [
                {
                    'name': 'Tomato',
                    'description': 'Fresh ripe country tomatoes',
                    'stock': 100,
                    'image_url': 'https://images.unsplash.com/photo-1607305387299-a3d9611cd469?w=400&h=300&fit=crop',
                    'prices': [('250g', 15), ('500g', 28), ('1kg', 52)]
                },
                {
                    'name': 'Carrot',
                    'description': 'Sweet organic carrots, rich in Vitamin A',
                    'stock': 150,
                    'image_url': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=300&fit=crop',
                    'prices': [('250g', 12), ('500g', 22), ('1kg', 40)]
                },
                {
                    'name': 'Potato',
                    'description': 'Fresh farm potatoes, perfect for any dish',
                    'stock': 200,
                    'image_url': 'https://images.unsplash.com/photo-1518977956812-cd3dbadaaf31?w=400&h=300&fit=crop',
                    'prices': [('250g', 10), ('500g', 18), ('1kg', 32)]
                },
                {
                    'name': 'Onion',
                    'description': 'Fresh red onions, kitchen essential',
                    'stock': 120,
                    'image_url': 'https://images.unsplash.com/photo-1618512496248-a07fe8cfe1cf?w=400&h=300&fit=crop',
                    'prices': [('250g', 11), ('500g', 20), ('1kg', 36)]
                },
                {
                    'name': 'Broccoli',
                    'description': 'Fresh green broccoli heads, superfood',
                    'stock': 80,
                    'image_url': 'https://images.unsplash.com/photo-1459411621453-7debff8f5c1b?w=400&h=300&fit=crop',
                    'prices': [('250g', 22), ('500g', 42), ('1kg', 78)]
                },
                {
                    'name': 'Spinach',
                    'description': 'Fresh organic spinach leaves, iron-rich',
                    'stock': 60,
                    'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&h=300&fit=crop',
                    'prices': [('250g', 14), ('500g', 26), ('1kg', 48)]
                },
                {
                    'name': 'Bell Pepper',
                    'description': 'Colorful mixed bell peppers (Red, Green, Yellow)',
                    'stock': 90,
                    'image_url': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=300&fit=crop',
                    'prices': [('250g', 18), ('500g', 34), ('1kg', 64)]
                },
                {
                    'name': 'Cucumber',
                    'description': 'Fresh garden cucumbers, crisp and refreshing',
                    'stock': 110,
                    'image_url': 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400&h=300&fit=crop',
                    'prices': [('250g', 13), ('500g', 24), ('1kg', 44)]
                },
                {
                    'name': 'Green Beans',
                    'description': 'Tender French beans, locally grown',
                    'stock': 70,
                    'image_url': 'https://images.unsplash.com/photo-1567373065684-8e8dbd7c7d4f?w=400&h=300&fit=crop',
                    'prices': [('250g', 16), ('500g', 30), ('1kg', 56)]
                },
                {
                    'name': 'Cabbage',
                    'description': 'Crisp green cabbage, perfect for salads',
                    'stock': 85,
                    'image_url': 'https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?w=400&h=300&fit=crop',
                    'prices': [('250g', 10), ('500g', 18), ('1kg', 34)]
                },
                {
                    'name': 'Cauliflower',
                    'description': 'Fresh white cauliflower, farm-fresh quality',
                    'stock': 75,
                    'image_url': 'https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?w=400&h=300&fit=crop',
                    'prices': [('250g', 14), ('500g', 26), ('1kg', 48)]
                },
                {
                    'name': 'Capsicum',
                    'description': 'Fresh green capsicum, crunchy and flavorful',
                    'stock': 95,
                    'image_url': 'https://images.unsplash.com/photo-1526470498-9ae73c665de8?w=400&h=300&fit=crop',
                    'prices': [('250g', 17), ('500g', 32), ('1kg', 60)]
                },
                {
                    'name': 'Garlic',
                    'description': 'Fresh garlic bulbs, aromatic and flavorful',
                    'stock': 130,
                    'image_url': 'https://images.unsplash.com/photo-1540148426945-6cf22a6b2571?w=400&h=300&fit=crop',
                    'prices': [('250g', 20), ('500g', 38), ('1kg', 72)]
                },
                {
                    'name': 'Ginger',
                    'description': 'Fresh ginger root, perfect for cooking',
                    'stock': 100,
                    'image_url': 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400&h=300&fit=crop',
                    'prices': [('250g', 18), ('500g', 34), ('1kg', 64)]
                },
                {
                    'name': 'Brinjal',
                    'description': 'Fresh purple brinjal (eggplant), tender and tasty',
                    'stock': 80,
                    'image_url': 'https://images.unsplash.com/photo-1615484477778-ca3b77940c95?w=400&h=300&fit=crop',
                    'prices': [('250g', 12), ('500g', 22), ('1kg', 40)]
                },
            ]

            for product_data in sample_products:
                product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    stock=product_data['stock'],
                    image_url=product_data['image_url'],
                    is_available=True
                )
                db.session.add(product)
                db.session.flush()

                for quantity, price in product_data['prices']:
                    price_option = ProductPrice(
                        product_id=product.id,
                        quantity=quantity,
                        price=price
                    )
                    db.session.add(price_option)

            db.session.commit()
            print('Sample products with pricing added to database')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
