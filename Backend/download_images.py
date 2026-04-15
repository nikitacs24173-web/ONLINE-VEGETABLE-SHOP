"""
Download real vegetable images from Wikipedia Commons
"""
import urllib.request
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

# Wikipedia Commons direct image URLs (real photos)
images = {
    'tomato.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Tomato_je.jpg/320px-Tomato_je.jpg',
    'carrot.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/CarrotDiversityDiversity.jpg/320px-CarrotDiversityDiversity.jpg',
    'potato.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Patates.jpg/320px-Patates.jpg',
    'onion.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Onion_%28Allium_cepa%29.jpg/320px-Onion_%28Allium_cepa%29.jpg',
    'broccoli.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Broccoli_and_cross_section_edit.jpg/320px-Broccoli_and_cross_section_edit.jpg',
    'spinach.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Spinach_leaves.jpg/320px-Spinach_leaves.jpg',
    'bell_pepper.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Bell_pepper_collection.jpg/320px-Bell_pepper_collection.jpg',
    'cucumber.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/ARS_cucumber.jpg/320px-ARS_cucumber.jpg',
    'green_beans.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Green_beans.jpg/320px-Green_beans.jpg',
    'cabbage.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Cabbage_and_cross_section.jpg/320px-Cabbage_and_cross_section.jpg',
    'cauliflower.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Cauliflower%2C_Bangladesh.jpg/320px-Cauliflower%2C_Bangladesh.jpg',
    'capsicum.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Green_Chilli.JPG/320px-Green_Chilli.JPG',
    'garlic.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Head_of_garlic.jpg/320px-Head_of_garlic.jpg',
    'ginger.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Ginger_in_Bangladesh.jpg/320px-Ginger_in_Bangladesh.jpg',
    'brinjal.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Eggplants_%28Solanum_melongena%29.jpg/320px-Eggplants_%28Solanum_melongena%29.jpg',
}

print("Downloading vegetable images...")
for filename, url in images.items():
    filepath = os.path.join(IMAGE_DIR, filename)
    try:
        urllib.request.urlretrieve(url, filepath)
        size = os.path.getsize(filepath)
        if size > 10000:  # Real images are > 10KB
            print(f"  ✓ {filename} ({size:,} bytes)")
        else:
            print(f"  ✗ {filename} - file too small ({size} bytes), download failed")
    except Exception as e:
        print(f"  ✗ {filename} - {e}")

print("\nDone! Check static/images folder for downloaded files.")
