from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('chrome-extension/icons', exist_ok=True)

def create_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = size // 8
    radius = size // 4
    
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=(102, 126, 234, 255)
    )
    
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        outline=(255, 255, 255, 255),
        width=max(1, size // 16)
    )
    
    try:
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "P"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    return img

sizes = {
    'icon16.png': 16,
    'icon48.png': 48,
    'icon128.png': 128,
}

for filename, size in sizes.items():
    icon = create_icon(size)
    path = f'chrome-extension/icons/{filename}'
    icon.save(path, 'PNG')
    print(f'Created: {path}')

print('Done!')
