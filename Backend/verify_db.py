"""
Database Verification Script - Shows all data in all tables
Run: python verify_db.py
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    'dbname': 'ovs',
    'user': 'postgres',
    'password': 'kapil123',
    'host': 'localhost',
    'port': '5432'
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("="*120)
    print("ONLINE VEGETABLE SHOP - DATABASE VERIFICATION")
    print("="*120)

    # List all tables
    print("\n" + "="*120)
    print("ALL TABLES IN DATABASE:")
    print("="*120)
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    for idx, table in enumerate(tables, 1):
        print(f"  {idx}. {table['table_name']}")

    # 1. USERS TABLE
    print("\n" + "="*120)
    print("USERS TABLE:")
    print("="*120)
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    print(f"\nTotal Users: {len(users)}\n")
    if users:
        print(f"{'ID':<5} {'Username':<20} {'Email':<35} {'Role':<10} {'Created At':<30}")
        print("-"*100)
        for user in users:
            print(f"{user['id']:<5} {user['username']:<20} {user['email']:<35} {user['role']:<10} {str(user['created_at']):<30}")

    # 2. PRODUCTS TABLE
    print("\n" + "="*120)
    print("PRODUCTS TABLE:")
    print("="*120)
    cur.execute("SELECT * FROM products ORDER BY id;")
    products = cur.fetchall()
    print(f"\nTotal Products: {len(products)}\n")
    if products:
        print(f"{'ID':<5} {'Name':<20} {'Stock':<8} {'Available':<12} {'Image URL':<45} {'Created At':<30}")
        print("-"*120)
        for product in products:
            print(f"{product['id']:<5} {product['name']:<20} {product['stock']:<8} {str(product['is_available']):<12} {product['image_url']:<45} {str(product['created_at']):<30}")

    # 3. PRODUCT PRICES TABLE
    print("\n" + "="*120)
    print("PRODUCT PRICES TABLE:")
    print("="*120)
    cur.execute("""
        SELECT pp.id, pp.product_id, pp.quantity, pp.price, p.name as product_name
        FROM product_prices pp 
        JOIN products p ON pp.product_id = p.id 
        ORDER BY pp.product_id, pp.quantity;
    """)
    prices = cur.fetchall()
    print(f"\nTotal Price Options: {len(prices)}\n")
    if prices:
        print(f"{'ID':<5} {'Product ID':<12} {'Product Name':<20} {'Quantity':<12} {'Price (Rs.)':<12}")
        print("-"*60)
        for price in prices:
            print(f"{price['id']:<5} {price['product_id']:<12} {price['product_name']:<20} {price['quantity']:<12} Rs.{float(price['price']):<10.2f}")

    # 4. CART TABLE
    print("\n" + "="*120)
    print("CART TABLE:")
    print("="*120)
    cur.execute("""
        SELECT c.id, c.user_id, c.product_id, c.price_id, c.quantity, c.added_at,
               u.username, p.name as product_name
        FROM cart c 
        JOIN users u ON c.user_id = u.id 
        JOIN products p ON c.product_id = p.id;
    """)
    cart = cur.fetchall()
    print(f"\nTotal Cart Items: {len(cart)}\n")
    if cart:
        print(f"{'ID':<5} {'User':<20} {'Product':<20} {'Price ID':<10} {'Qty':<5} {'Added At':<30}")
        print("-"*90)
        for item in cart:
            print(f"{item['id']:<5} {item['username']:<20} {item['product_name']:<20} {item['price_id']:<10} {item['quantity']:<5} {str(item['added_at']):<30}")
    else:
        print("  (Cart is empty)")

    # 5. ORDERS TABLE
    print("\n" + "="*120)
    print("ORDERS TABLE:")
    print("="*120)
    cur.execute("""
        SELECT o.id, o.user_id, o.total_amount, o.status, o.order_date,
               u.username, u.email
        FROM orders o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.order_date DESC;
    """)
    orders = cur.fetchall()
    print(f"\nTotal Orders: {len(orders)}\n")
    if orders:
        print(f"{'ID':<5} {'User':<20} {'Total Amount':<15} {'Status':<15} {'Order Date':<30}")
        print("-"*85)
        for order in orders:
            print(f"{order['id']:<5} {order['username']:<20} Rs.{float(order['total_amount']):<12.2f} {order['status']:<15} {str(order['order_date']):<30}")
    else:
        print("  (No orders yet)")

    # 6. ORDER ITEMS TABLE
    print("\n" + "="*120)
    print("ORDER ITEMS TABLE:")
    print("="*120)
    cur.execute("""
        SELECT oi.id, oi.order_id, oi.product_id, oi.quantity, oi.price,
               p.name as product_name
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id;
    """)
    order_items = cur.fetchall()
    print(f"\nTotal Order Items: {len(order_items)}\n")
    if order_items:
        print(f"{'ID':<5} {'Order ID':<10} {'Product':<20} {'Qty':<5} {'Price (Rs.)':<12}")
        print("-"*52)
        for item in order_items:
            print(f"{item['id']:<5} {item['order_id']:<10} {item['product_name']:<20} {item['quantity']:<5} Rs.{float(item['price']):<10.2f}")
    else:
        print("  (No order items yet)")

    # 7. PAYMENTS TABLE
    print("\n" + "="*120)
    print("PAYMENTS TABLE:")
    print("="*120)
    cur.execute("""
        SELECT p.id, p.order_id, p.user_id, p.payment_method, p.utr_number, 
               p.amount, p.status, p.payment_date,
               u.username, u.email
        FROM payments p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.payment_date DESC;
    """)
    payments = cur.fetchall()
    print(f"\nTotal Payments: {len(payments)}\n")
    if payments:
        print(f"{'ID':<5} {'Order ID':<10} {'User':<20} {'Amount':<12} {'UTR Number':<35} {'Status':<12} {'Date':<30}")
        print("-"*124)
        for payment in payments:
            print(f"{payment['id']:<5} {payment['order_id']:<10} {payment['username']:<20} Rs.{float(payment['amount']):<10.2f} {payment['utr_number']:<35} {payment['status']:<12} {str(payment['payment_date']):<30}")
    else:
        print("  (No payments yet)")

    print("\n" + "="*120)
    print("VERIFICATION COMPLETE!")
    print("="*120)
    print("\nDatabase Summary:")
    print(f"  - Users: {len(users)}")
    print(f"  - Products: {len(products)}")
    print(f"  - Price Options: {len(prices)}")
    print(f"  - Cart Items: {len(cart)}")
    print(f"  - Orders: {len(orders)}")
    print(f"  - Order Items: {len(order_items)}")
    print(f"  - Payments: {len(payments)}")
    print("="*120)

    cur.close()
    conn.close()

except psycopg2.Error as e:
    print(f"\nERROR: Database connection or query failed!")
    print(f"Details: {e}")
    print("\nPlease check:")
    print("  1. PostgreSQL server is running")
    print("  2. Database 'ovs' exists")
    print("  3. Username and password are correct")
    print(f"  4. Connection details in DB_CONFIG are correct")
    print("="*120)
    exit(1)
