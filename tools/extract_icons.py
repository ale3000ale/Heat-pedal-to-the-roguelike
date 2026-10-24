from PIL import Image
import numpy as np
import os

os.makedirs('frontend/static/icons', exist_ok=True)
os.makedirs('frontend/static/images', exist_ok=True)

img = Image.open('assets/set icone.jpg').convert('RGBA')
w, h = img.size

# Precise bounding boxes for the key icons in set icone.jpg (1300x996)
# Note: we exclude the alamy watermark at the bottom (y > 900)
icon_boxes = {
    'flags_crossed': (10, 0, 230, 140),
    'flags_crossed_thin': (280, 0, 470, 135),
    'pistons': (470, 50, 670, 290),
    'wings_left': (640, 25, 800, 115),
    'wings_right': (845, 25, 1000, 115),
    'trophy_grand': (0, 140, 135, 345),
    'trophy_sleek': (180, 150, 285, 350),
    'trophy_winged': (300, 150, 445, 350),
    'f1_car_red': (695, 135, 885, 285),
    'spark_plug': (935, 120, 988, 335),
    'wrenches': (10, 375, 155, 500),
    'race_ribbon': (195, 370, 430, 438),
    'helmet_red': (450, 300, 545, 420),
    'crown': (555, 330, 630, 390),
    'car_speed_flag': (650, 315, 855, 485),
    'speedometer': (880, 385, 988, 520),
    'flags_wavy_left': (20, 520, 205, 660),
    'flags_wavy_center': (230, 540, 420, 690),
    'flags_classic': (425, 460, 630, 670),
    'tires': (0, 740, 140, 885),
    'stopwatch': (165, 700, 288, 890),
    'wheel_ribbon': (565, 650, 820, 890),
    'laurel_wreath': (825, 645, 1000, 870),
}

def make_transparent(crop_img):
    # Convert near white pixels to transparent, with smooth alpha edge
    data = np.array(crop_img, dtype=float)
    # Brightness threshold
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
    # Distance from pure white
    dist = np.sqrt((255 - r)**2 + (255 - g)**2 + (255 - b)**2)
    # If dist < 15, fully transparent
    # If dist between 15 and 60, linear alpha
    alpha = np.clip((dist - 10) / 45.0, 0.0, 1.0) * 255.0
    data[:, :, 3] = alpha
    # Tidy up pixels
    data = np.uint8(data)
    result = Image.fromarray(data, 'RGBA')
    # Auto-trim transparent borders
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    return result

for name, box in icon_boxes.items():
    cropped = img.crop(box)
    trans = make_transparent(cropped)
    save_path = f'frontend/static/icons/{name}.png'
    trans.save(save_path, 'PNG')
    print(f'Saved {name} -> {trans.size}')

print('Icon extraction complete!')
