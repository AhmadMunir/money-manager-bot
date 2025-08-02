# Simple Icon Creator
# Creates a basic ICO file for the executable

from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_icon():
    """Create a simple MonMan Bot icon"""
    # Create image
    size = (64, 64)
    img = Image.new('RGBA', size, (0, 123, 255, 255))  # Blue background
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([2, 2, size[0]-3, size[1]-3], outline=(255, 255, 255, 255), width=2)
    
    # Draw "MB" text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    text = "MB"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Draw $ symbol
    dollar_font = ImageFont.load_default()
    draw.text((size[0]-15, 5), "$", fill=(255, 255, 0, 255), font=dollar_font)
    
    # Save as ICO with multiple sizes
    os.makedirs("assets", exist_ok=True)
    img.save("assets/icon.ico", format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
    print("✅ Icon created: assets/icon.ico")

if __name__ == "__main__":
    try:
        create_simple_icon()
    except ImportError:
        print("❌ Pillow not installed. Install with: pip install Pillow")
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        # Create minimal placeholder
        os.makedirs("assets", exist_ok=True)
        with open("assets/icon.ico", "wb") as f:
            # Minimal ICO header for 16x16 icon
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00\x68\x05\x00\x00\x16\x00\x00\x00')
            f.write(b'\x00' * 1384)  # Placeholder data
        print("✅ Placeholder icon created: assets/icon.ico")
