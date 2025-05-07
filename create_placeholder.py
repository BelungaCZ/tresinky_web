from PIL import Image, ImageDraw, ImageFont
import os

# Create a 300x300 gray image
img = Image.new('RGB', (300, 300), color='gray')
draw = ImageDraw.Draw(img)

# Add text
try:
    font = ImageFont.truetype("Arial", 20)
except IOError:
    font = ImageFont.load_default()

text = "Image not available"
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Center the text
x = (300 - text_width) // 2
y = (300 - text_height) // 2

draw.text((x, y), text, fill='white', font=font)

# Create directory if it doesn't exist
os.makedirs('static/img', exist_ok=True)

# Save the image
img.save('static/img/placeholder.jpg') 