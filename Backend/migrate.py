"""
PostgreSQL Migration Script - Fixes schema and seeds 15 vegetables
Run: python migrate.py
"""
import psycopg2
from psycopg2.extras import execute_values

# Database connection
DB_CONFIG = {
    'dbname': 'ovs',
    'user': 'postgres',
    'password': 'kapil123',
    'host': 'localhost',
    'port': '5432'
}

conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = True
cur = conn.cursor()

print("Connected to PostgreSQL database 'ovs'")

# ==================== STEP 1: Fix Schema ====================
print("\n--- Fixing Database Schema ---")

# Create product_prices table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS product_prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity VARCHAR(20) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    CONSTRAINT _product_quantity_uc UNIQUE (product_id, quantity)
);
""")
print("✓ product_prices table created/exists")

# Create payments table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    payment_method VARCHAR(50) DEFAULT 'upi',
    utr_number VARCHAR(100),
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    payment_date TIMESTAMP DEFAULT NOW()
);
""")
print("✓ payments table created/exists")

# Add price_id to cart table if not exists
cur.execute("""
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'cart' AND column_name = 'price_id';
""")
if not cur.fetchone():
    cur.execute("ALTER TABLE cart ADD COLUMN price_id INTEGER REFERENCES product_prices(id);")
    print("✓ Added price_id column to cart")
else:
    print("✓ price_id column already exists in cart")

# Drop old price column from products table if it exists
cur.execute("""
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'products' AND column_name = 'price';
""")
if cur.fetchone():
    cur.execute("ALTER TABLE products DROP COLUMN price;")
    print("✓ Dropped old price column from products")
else:
    print("✓ Old price column already removed from products")

# ==================== STEP 2: Clean Old Data ====================
print("\n--- Cleaning Old Data ---")

cur.execute("DELETE FROM payments;")
cur.execute("DELETE FROM order_items;")
cur.execute("DELETE FROM orders;")
cur.execute("DELETE FROM cart;")
cur.execute("DELETE FROM product_prices;")
cur.execute("DELETE FROM products;")
print("✓ Old data cleared")

# ==================== STEP 3: Seed 15 Vegetables ====================
print("\n--- Seeding 15 Vegetables with Images & Prices ---")

vegetables = [
    {
        'name': 'Tomato',
        'description': 'Fresh ripe country tomatoes',
        'stock': 100,
        'image_url': '/static/images/tomato.svg',
        'prices': [('250g', 15), ('500g', 28), ('1kg', 52), ('1.25kg', 65), ('1.5kg', 78), ('1.75kg', 91), ('2kg', 104)]
    },
    {
        'name': 'Carrot',
        'description': 'Sweet organic carrots, rich in Vitamin A',
        'stock': 150,
        'image_url': '/static/images/carrot.svg',
        'prices': [('250g', 12), ('500g', 22), ('1kg', 40), ('1.25kg', 50), ('1.5kg', 60), ('1.75kg', 70), ('2kg', 80)]
    },
    {
        'name': 'Potato',
        'description': 'Fresh farm potatoes, perfect for any dish',
        'stock': 200,
        'image_url': '/static/images/potato.svg',
        'prices': [('250g', 10), ('500g', 18), ('1kg', 32), ('1.25kg', 40), ('1.5kg', 48), ('1.75kg', 56), ('2kg', 64)]
    },
    {
        'name': 'Onion',
        'description': 'Fresh red onions, kitchen essential',
        'stock': 120,
        'image_url': '/static/images/onion.svg',
        'prices': [('250g', 11), ('500g', 20), ('1kg', 36), ('1.25kg', 45), ('1.5kg', 54), ('1.75kg', 63), ('2kg', 72)]
    },
    {
        'name': 'Broccoli',
        'description': 'Fresh green broccoli heads, superfood',
        'stock': 80,
        'image_url': '/static/images/broccoli.svg',
        'prices': [('250g', 22), ('500g', 42), ('1kg', 78), ('1.25kg', 98), ('1.5kg', 117), ('1.75kg', 137), ('2kg', 156)]
    },
    {
        'name': 'Spinach',
        'description': 'Fresh organic spinach leaves, iron-rich',
        'stock': 60,
        'image_url': '/static/images/spinach.svg',
        'prices': [('250g', 14), ('500g', 26), ('1kg', 48), ('1.25kg', 60), ('1.5kg', 72), ('1.75kg', 84), ('2kg', 96)]
    },
    {
        'name': 'Bell Pepper',
        'description': 'Colorful mixed bell peppers (Red, Green, Yellow)',
        'stock': 90,
        'image_url': '/static/images/bell_pepper.svg',
        'prices': [('250g', 18), ('500g', 34), ('1kg', 64), ('1.25kg', 80), ('1.5kg', 96), ('1.75kg', 112), ('2kg', 128)]
    },
    {
        'name': 'Cucumber',
        'description': 'Fresh garden cucumbers, crisp and refreshing',
        'stock': 110,
        'image_url': '/static/images/cucumber.svg',
        'prices': [('250g', 13), ('500g', 24), ('1kg', 44), ('1.25kg', 55), ('1.5kg', 66), ('1.75kg', 77), ('2kg', 88)]
    },
    {
        'name': 'Green Beans',
        'description': 'Tender French beans, locally grown',
        'stock': 70,
        'image_url': '/static/images/green_beans.svg',
        'prices': [('250g', 16), ('500g', 30), ('1kg', 56), ('1.25kg', 70), ('1.5kg', 84), ('1.75kg', 98), ('2kg', 112)]
    },
    {
        'name': 'Cabbage',
        'description': 'Crisp green cabbage, perfect for salads',
        'stock': 85,
        'image_url': '/static/images/cabbage.svg',
        'prices': [('250g', 10), ('500g', 18), ('1kg', 34), ('1.25kg', 43), ('1.5kg', 51), ('1.75kg', 60), ('2kg', 68)]
    },
    {
        'name': 'Capsicum',
        'description': 'Fresh green capsicum, crunchy and flavorful',
        'stock': 95,
        'image_url': '/static/images/capsicum.svg',
        'prices': [('250g', 17), ('500g', 32), ('1kg', 60), ('1.25kg', 75), ('1.5kg', 90), ('1.75kg', 105), ('2kg', 120)]
    },
    {
        'name': 'Garlic',
        'description': 'Fresh garlic bulbs, aromatic and flavorful',
        'stock': 130,
        'image_url': '/static/images/garlic.svg',
        'prices': [('250g', 20), ('500g', 38), ('1kg', 72), ('1.25kg', 90), ('1.5kg', 108), ('1.75kg', 126), ('2kg', 144)]
    },
    {
        'name': 'Ginger',
        'description': 'Fresh ginger root, perfect for cooking',
        'stock': 100,
        'image_url': '/static/images/ginger.svg',
        'prices': [('250g', 18), ('500g', 34), ('1kg', 64), ('1.25kg', 80), ('1.5kg', 96), ('1.75kg', 112), ('2kg', 128)]
    },
    {
        'name': 'Brinjal',
        'description': 'Fresh purple brinjal (eggplant), tender and tasty',
        'stock': 80,
        'image_url': '/static/images/brinjal.svg',
        'prices': [('250g', 12), ('500g', 22), ('1kg', 40), ('1.25kg', 50), ('1.5kg', 60), ('1.75kg', 70), ('2kg', 80)]
    },
]

for veg in vegetables:
    # Insert product
    cur.execute("""
        INSERT INTO products (name, description, stock, image_url, is_available, created_at)
        VALUES (%(name)s, %(description)s, %(stock)s, %(image_url)s, true, NOW())
        RETURNING id;
    """, veg)
    product_id = cur.fetchone()[0]

    # Insert prices
    for quantity, price in veg['prices']:
        cur.execute("""
            INSERT INTO product_prices (product_id, quantity, price)
            VALUES (%s, %s, %s);
        """, (product_id, quantity, price))

    print(f"  ✓ {veg['name']} added with prices: 250g=₹{veg['prices'][0][1]}, 500g=₹{veg['prices'][1][1]}, 1kg=₹{veg['prices'][2][1]}")

# ==================== STEP 4: Verify ====================
cur.execute("SELECT COUNT(*) FROM products;")
product_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM product_prices;")
price_count = cur.fetchone()[0]

print(f"\n{'='*50}")
print(f"✓ Migration Complete!")
print(f"  Products: {product_count}")
print(f"  Price Options: {price_count}")
print(f"{'='*50}")

cur.close()
conn.close()
print("\nDatabase connection closed.")
