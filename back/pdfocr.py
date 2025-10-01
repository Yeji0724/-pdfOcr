# pdfocr.py (DPI 300 유지 및 최종 안정화 버전)

import fitz # PyMuPDF
from PIL import Image
import io
import numpy as np
import re
import pytesseract
import easyocr
import torch
from paddleocr import PaddleOCR 
from pykospacing import Spacing

# --- 글로벌 객체 초기화 ---
# Tesseract 경로 설정 (필수)
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

try:
    # EasyOCR 초기화
    easy_reader = easyocr.Reader(['ko', 'en'], gpu=torch.cuda.is_available())
except:
    easy_reader = None

# 🚨 최종 조치: PaddleOCR 강제 비활성화 (고질적인 런타임 오류 차단)
paddle_reader = None 

try:
    # 띄어쓰기 모델 초기화
    spacing_model = Spacing()
except:
    spacing_model = None

# --- 헬퍼 함수 ---
def clean_ocr_text(raw_text):
    # OCR 결과 정리 (한글 뒤 공백 제거, 중복 줄바꿈/공백 제거)
    raw_text = re.sub(r'(?<=[가-힣])\s(?=[가-힣])', '', raw_text)
    raw_text = re.sub(r'\n+', '\n', raw_text)
    raw_text = re.sub(r'[ ]{2,}', ' ', raw_text)
    return raw_text.strip()

def correct_spacing(text):
    # 띄어쓰기 교정 적용
    if spacing_model is None or not text.strip():
        return text
    text_no_space = text.replace(" ", "")
    return spacing_model(text_no_space)

def run_ocr_engine(engine_name: str, pil_img: Image.Image) -> str:
    np_img = np.array(pil_img)
    
    if engine_name == 'pytesseract':
        text = pytesseract.image_to_string(pil_img, lang='kor') 
        return text if text else "PyTesseract: 텍스트를 찾지 못함"
    
    elif engine_name == 'easyocr':
        if not easy_reader:
            return "ERROR: EasyOCR 로드 실패"
        
        # EasyOCR은 detail=0으로 최종 텍스트만 추출
        result = easy_reader.readtext(np_img, detail=0)
        
        return "\n".join(result) if result else "EasyOCR: 문자 영역을 전혀 탐지하지 못함"
    
    elif engine_name == 'paddleocr':
        # 🚨 PaddleOCR 강제 비활성화로 인해 바로 오류 메시지 반환
        return "ERROR: PaddleOCR 로드 실패 (임시 비활성화됨)"
        
    return f"ERROR: 알 수 없는 OCR 엔진 '{engine_name}'입니다."

def pdf_to_text_with_ocr(pdf_bytes, engine_name: str):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []
    for page in doc:
        text = page.get_text("text").strip()
        blocks = page.get_text("blocks")
        image_blocks = [b for b in blocks if b[6] == 1]

        extracted_text = ""
        if len(image_blocks) == 0 and len(text) > 10: 
            extracted_text = text
        else:
            # ✅ DPI 300 유지 (사용자 요청 및 안정적인 값)
            pix = page.get_pixmap(dpi=300) 
            img_bytes = pix.tobytes(output="png")
            
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB").convert('L') 
            
            # 이미지 이진화 임계값 150 유지 (대비 극대화)
            pil_img = pil_img.point(lambda x: 0 if x < 150 else 255)
            
            # 디버깅 코드 (이미지 저장)는 유지
            output_path = f"debug_page_{page.number}_{engine_name}.png"
            print(f"이미지 저장 경로: {output_path}")
            pil_img.save(output_path) 
            
            extracted_text = run_ocr_engine(engine_name, pil_img)
        full_text.append(extracted_text)

    doc.close()
    
    final_text = []
    for t in full_text:
        cleaned_t = clean_ocr_text(t)
        
        try:
            # 🚨 Pykospacing 보호 코드 적용
            spaced_t = correct_spacing(cleaned_t)
            final_text.append(spaced_t)
        except Exception as e:
            # Pykospacing 오류 발생 시 원본 텍스트 사용
            print(f"🚨 Pykospacing 처리 중 오류 발생: {e}. 원본 텍스트 사용.")
            final_text.append(cleaned_t) 
            
    return "\n\n".join(final_text)