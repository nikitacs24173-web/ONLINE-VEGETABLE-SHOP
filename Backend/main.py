from flask import Blueprint, render_template, request
from backend.models.product import Product

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with product listing and search"""
    search_query = request.args.get('search', '')
    
    if search_query:
        products = Product.query.filter(
            Product.name.ilike(f'%{search_query}%'),
            Product.is_available == True
        ).all()
    else:
        products = Product.query.filter_by(is_available=True).all()
    
    return render_template('index.html', products=products, search_query=search_query)
