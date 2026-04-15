from backend.utils.database import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one product per user in cart
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'price': float(self.product.price) if self.product else 0,
            'quantity': self.quantity,
            'subtotal': float(self.product.price * self.quantity) if self.product else 0,
            'added_at': self.added_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Cart {self.id} - User: {self.user_id}>'
