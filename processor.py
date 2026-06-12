import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

def mock_vision_api(image_bytes):
    # 실제로는 GCP Vision API에 이미지를 전송하고 결과를 받아오는 로직이 들어갑니다.
    # 지금은 테스트를 위해 고정된 박스(못생긴 글씨 위치)를 반환합니다.
    return [
        {"text": "Hello World", "bbox": (100, 150, 310, 190)},
        {"text": "안녕 파이썬", "bbox": (100, 220, 290, 260)}
    ]

def process_image(image_bytes: bytes, font_path="C:/Windows/Fonts/malgun.ttf") -> bytes:
    # 1. 바이트를 OpenCV 이미지로 디코딩
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Cannot decode image")

    # 2. Vision API 호출 (Mock)
    ocr_results = mock_vision_api(image_bytes)
    
    # 3. 텍스트 지우기 (OpenCV Inpainting)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for item in ocr_results:
        x1, y1, x2, y2 = item['bbox']
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    result_img = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    
    # 4. 새로운 폰트 렌더링 (Pillow)
    # OpenCV(BGR) -> Pillow(RGB)
    color_converted = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(color_converted)
    draw = ImageDraw.Draw(pil_img)
    
    for item in ocr_results:
        text = item['text']
        x1, y1, x2, y2 = item['bbox']
        target_width = x2 - x1
        target_height = y2 - y1
        
        font_size = 10
        font = None
        while True:
            try:
                temp_font = ImageFont.truetype(font_path, font_size)
                left, top, right, bottom = draw.textbbox((0, 0), text, font=temp_font)
                width = right - left
                height = bottom - top
                if width > target_width or height > target_height:
                    break
                font = temp_font
                font_size += 1
            except Exception:
                font = ImageFont.load_default()
                break
                
        if font is None:
            try:
                font = ImageFont.truetype(font_path, 10)
            except:
                font = ImageFont.load_default()
                
        # 렌더링: 검은색 (혹은 원하는 귀여운 색상)으로 그리기
        draw.text((x1, y1), text, fill=(0, 0, 0), font=font)
        
    # 5. 결과를 Bytes로 변환하여 반환
    out_io = io.BytesIO()
    pil_img.save(out_io, format="JPEG")
    return out_io.getvalue()
