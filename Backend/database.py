from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        seed_initial_data()

def seed_initial_data():
    """Seed initial data if database is empty"""
    from backend.models.user import User
    from backend.models.product import Product
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@ovs.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin user created: admin/admin123')
    
    # Add sample products if none exist
    if Product.query.count() == 0:
        sample_products = [
            Product(name='Tomato', description='Fresh ripe tomatoes', price=2.99, stock=100, is_available=True),
            Product(name='Carrot', description='Organic carrots', price=1.49, stock=150, is_available=True),
            Product(name='Potato', description='Fresh potatoes', price=0.99, stock=200, is_available=True),
            Product(name='Onion', description='Red onions', price=1.29, stock=120, is_available=True),
            Product(name='Broccoli', description='Fresh broccoli heads', price=2.49, stock=80, is_available=True),
            Product(name='Spinach', description='Fresh spinach leaves', price=1.99, stock=60, is_available=True),
            Product(name='Bell Pepper', description='Colorful bell peppers', price=3.49, stock=90, is_available=True),
            Product(name='Cucumber', description='Fresh cucumbers', price=1.79, stock=110, is_available=True),
        ]
        db.session.add_all(sample_products)
        db.session.commit()
        print('✓ Sample products added to database')
