from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.models.product import Product
from backend.models.order import Order
from backend.utils.database import db
from backend.utils.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    products = Product.query.all()
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin/dashboard.html', products=products, orders=orders)

@admin_bp.route('/product/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            stock=int(request.form.get('stock')),
            image_url=request.form.get('image_url'),
            is_available=request.form.get('is_available') == 'on'
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/product_form.html', product=None)

@admin_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Edit existing product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.image_url = request.form.get('image_url')
        product.is_available = request.form.get('is_available') == 'on'
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/product_form.html', product=product)

@admin_bp.route('/product/delete/<int:product_id>')
@admin_required
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/order/<int:order_id>/update', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order_id} status updated to {new_status}!', 'success')
    
    return redirect(url_for('admin.admin_dashboard'))
