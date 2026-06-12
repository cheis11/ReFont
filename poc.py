import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request

# --- Helper Functions for Assets ---
def download_font(font_path):
    pass # No need to download, we will use a system font

def create_dummy_image(image_path):
    if not os.path.exists(image_path):
        print(f"Creating dummy image at {image_path}...")
        # Create a light gray background
        img = Image.new('RGB', (600, 400), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        font_path = "C:/Windows/Fonts/malgun.ttf"
        try:
            font = ImageFont.truetype(font_path, 40)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw some dummy text
        draw.text((100, 150), "Hello World", fill=(50, 50, 50), font=font)
        draw.text((100, 220), "안녕 파이썬", fill=(50, 50, 50), font=font)
        img.save(image_path)
        print("Dummy image created.")

# --- Mock Vision API ---
def mock_vision_api(image_path):
    # Returns a list of dictionaries with 'text' and 'bbox' (x1, y1, x2, y2)
    # These coordinates are roughly where we drew the text in create_dummy_image
    return [
        {"text": "Hello World", "bbox": (100, 150, 310, 190)},
        {"text": "안녕 파이썬", "bbox": (100, 220, 290, 260)}
    ]

# --- Core Pipeline Functions ---
def erase_text(image_path, ocr_results, output_path):
    print("Erasing text using OpenCV inpainting...")
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")
    
    # Create an empty mask
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    for item in ocr_results:
        x1, y1, x2, y2 = item['bbox']
        # Draw filled rectangle on mask
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    
    # Dilate the mask to ensure we cover the edges of the text
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Inpaint
    result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    cv2.imwrite(output_path, result)
    print(f"Erased image saved to {output_path}")

def render_text(image_path, ocr_results, font_path, output_path):
    print("Rendering text using Pillow...")
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    for item in ocr_results:
        text = item['text']
        x1, y1, x2, y2 = item['bbox']
        target_width = x2 - x1
        target_height = y2 - y1
        
        # Dynamic font sizing
        font_size = 10
        font = None
        while True:
            try:
                temp_font = ImageFont.truetype(font_path, font_size)
                # getbbox returns (left, top, right, bottom)
                left, top, right, bottom = draw.textbbox((0, 0), text, font=temp_font)
                width = right - left
                height = bottom - top
                
                if width > target_width or height > target_height:
                    break
                font = temp_font
                font_size += 1
            except Exception as e:
                print(f"Error loading font: {e}")
                font = ImageFont.load_default()
                break
        
        if font is None:
            # Fallback if even size 10 is too big (rare)
            font = ImageFont.truetype(font_path, 10)
            
        # Draw the text at the original position
        # We can center it vertically or horizontally within the bbox if needed
        # For now, just place it at (x1, y1)
        draw.text((x1, y1), text, fill=(0, 0, 255), font=font) # Draw in Blue to see the difference
    
    img.save(output_path)
    print(f"Final image saved to {output_path}")

def main():
    font_path = "C:/Windows/Fonts/malgun.ttf"
    original_img = "sample_input.jpg"
    erased_img = "sample_erased.jpg"
    final_img = "sample_final.jpg"
    
    # 1. Setup assets
    download_font(font_path)
    create_dummy_image(original_img)
    
    # 2. Extract Text (Mocked)
    ocr_results = mock_vision_api(original_img)
    print(f"OCR Results: {ocr_results}")
    
    # 3. Erase Text
    erase_text(original_img, ocr_results, erased_img)
    
    # 4. Render Text
    render_text(erased_img, ocr_results, font_path, final_img)
    
    print("Pipeline test completed successfully!")

if __name__ == "__main__":
    main()
