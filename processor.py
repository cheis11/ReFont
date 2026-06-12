import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import random
import textwrap

def mock_vision_api(image_bytes):
    # 실제 환경에서는 구글 Cloud Vision API 등을 통해 이미지 내 텍스트 전체를 추출합니다.
    # 지금은 테스트용으로 긴 문장을 반환합니다.
    return "안녕하세요! 제 삐뚤빼뚤한 손글씨를 인식해서, 정말 제가 정성들여 쓴 것처럼 예쁘고 똑바르게 바꿔주세요. 텍스트로 추출한 뒤에 다시 그리는 마법입니다!"

def process_image(image_bytes: bytes, font_path="nanum_pen.ttf") -> bytes:
    # 1. 텍스트 추출 (OCR)
    # image_bytes는 실제로 Vision API로 넘어가서 텍스트를 추출하는 데 사용됩니다.
    extracted_text = mock_vision_api(image_bytes)
    
    # 2. 깨끗한 종이 캔버스 생성 (따뜻한 미색 배경)
    canvas_width, canvas_height = 800, 600
    canvas = Image.new('RGB', (canvas_width, canvas_height), color=(250, 248, 240))
    
    # 3. 폰트 로드
    base_font_size = 40
    try:
        font = ImageFont.truetype(font_path, base_font_size)
    except IOError:
        font = ImageFont.load_default()
        base_font_size = 20

    # 4. 텍스트 줄바꿈 처리 (가로 크기에 맞게)
    # 실제 폰트 폭을 기반으로 정확히 래핑하려면 복잡하지만, 여기서는 글자 수로 대략 나눕니다.
    max_chars_per_line = 25
    wrapped_lines = textwrap.wrap(extracted_text, width=max_chars_per_line)
    
    # 5. Humanize (사람이 쓴 것처럼 흔들기) 렌더링
    start_x = 50
    start_y = 50
    line_spacing = base_font_size * 1.5
    
    current_y = start_y
    
    for line in wrapped_lines:
        current_x = start_x
        
        for char in line:
            if char == ' ':
                current_x += base_font_size * 0.4  # 띄어쓰기 간격
                continue
                
            # 사람의 손떨림(Humanize) 효과 수치 계산
            # 1) 상하좌우 미세 흔들림
            offset_x = random.uniform(-1.5, 1.5)
            offset_y = random.uniform(-2.0, 2.0)
            
            # 2) 글자 크기 미세 변화 (폰트 사이즈를 동적으로 바꾸기 어려우므로 회전으로 대체 가능하지만, 여기서는 y축 변동으로 충분히 느낌이 납니다)
            
            # 개별 글자를 투명 캔버스에 그려서 회전(기울기 흔들림) 적용
            char_canvas = Image.new('RGBA', (base_font_size*2, base_font_size*2), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_canvas)
            char_draw.text((base_font_size//2, base_font_size//2), char, fill=(30, 30, 40, 255), font=font)
            
            # 미세 회전 (-3도 ~ 3도)
            angle = random.uniform(-3.0, 3.0)
            rotated_char = char_canvas.rotate(angle, resample=Image.BICUBIC, expand=1)
            
            # 메인 캔버스에 붙이기 (투명도 유지)
            paste_x = int(current_x + offset_x) - (base_font_size//2)
            paste_y = int(current_y + offset_y) - (base_font_size//2)
            
            canvas.paste(rotated_char, (paste_x, paste_y), rotated_char)
            
            # 다음 글자 좌표로 이동 (글자의 실제 폭만큼)
            left, top, right, bottom = char_draw.textbbox((0, 0), char, font=font)
            char_width = right - left
            current_x += char_width + random.uniform(0, 2) # 자간(글씨 간격)도 살짝 랜덤
            
        # 다음 줄로 이동
        current_y += line_spacing + random.uniform(-2, 2) # 줄 간격도 살짝 랜덤
        
    # 6. 결과를 Bytes로 변환하여 반환
    out_io = io.BytesIO()
    canvas.save(out_io, format="JPEG", quality=95)
    return out_io.getvalue()
