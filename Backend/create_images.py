"""
Create SVG vegetable images with beautiful gradients and emoji
"""
import os

IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

# Beautiful gradient combinations for each vegetable
vegetables = {
    'tomato.svg': {
        'bg1': '#ff6b6b', 'bg2': '#c0392b', 'emoji': '🍅', 'name': 'Tomato'
    },
    'carrot.svg': {
        'bg1': '#f39c12', 'bg2': '#e67e22', 'emoji': '🥕', 'name': 'Carrot'
    },
    'potato.svg': {
        'bg1': '#d4a574', 'bg2': '#8B6914', 'emoji': '🥔', 'name': 'Potato'
    },
    'onion.svg': {
        'bg1': '#9b59b6', 'bg2': '#6c3483', 'emoji': '🧅', 'name': 'Onion'
    },
    'broccoli.svg': {
        'bg1': '#27ae60', 'bg2': '#1e8449', 'emoji': '🥦', 'name': 'Broccoli'
    },
    'spinach.svg': {
        'bg1': '#2ecc71', 'bg2': '#229954', 'emoji': '🥬', 'name': 'Spinach'
    },
    'bell_pepper.svg': {
        'bg1': '#e74c3c', 'bg2': '#f39c12', 'emoji': '🫑', 'name': 'Bell Pepper'
    },
    'cucumber.svg': {
        'bg1': '#58d68d', 'bg2': '#27ae60', 'emoji': '🥒', 'name': 'Cucumber'
    },
    'green_beans.svg': {
        'bg1': '#52be80', 'bg2': '#1abc9c', 'emoji': '🫘', 'name': 'Green Beans'
    },
    'cabbage.svg': {
        'bg1': '#82e0aa', 'bg2': '#58d68d', 'emoji': '🥬', 'name': 'Cabbage'
    },
    'cauliflower.svg': {
        'bg1': '#f5f5dc', 'bg2': '#d5d5d5', 'emoji': '🤍', 'name': 'Cauliflower'
    },
    'capsicum.svg': {
        'bg1': '#2ecc71', 'bg2': '#27ae60', 'emoji': '🌶️', 'name': 'Capsicum'
    },
    'garlic.svg': {
        'bg1': '#f9e79f', 'bg2': '#f5cba7', 'emoji': '🧄', 'name': 'Garlic'
    },
    'ginger.svg': {
        'bg1': '#d4a76a', 'bg2': '#c19a6b', 'emoji': '🫚', 'name': 'Ginger'
    },
    'brinjal.svg': {
        'bg1': '#6c3483', 'bg2': '#4a235a', 'emoji': '🍆', 'name': 'Brinjal'
    },
}

for filename, veg in vegetables.items():
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{veg['bg1']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{veg['bg2']};stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="400" height="300" fill="url(#bg)" />
    <text x="200" y="160" font-size="100" text-anchor="middle" dominant-baseline="central">{veg['emoji']}</text>
    <text x="200" y="240" font-size="24" font-family="Arial, sans-serif" font-weight="bold" fill="white" text-anchor="middle" opacity="0.9">{veg['name']}</text>
</svg>'''
    
    filepath = os.path.join(IMAGE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"✓ Created {filename}")

print(f"\n{len(vegetables)} vegetable images created in {IMAGE_DIR}")
