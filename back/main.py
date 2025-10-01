# main.py (최종)
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from pdfocr import pdf_to_text_with_ocr

# FastAPI 앱 생성
app = FastAPI(title="PDF 텍스트 추출 및 띄어쓰기 교정 서비스")

# CORS 설정
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚨 엔드포인트: /extract
@app.post("/extract")
async def extract_text(
    files: list[UploadFile] = File(...),
    # ocr_engine 쿼리 매개변수는 그대로 유지
    ocr_engine: str = Query("paddle", pattern="^(paddle|pytesseract|easyocr)$")
):
    """
    다중 PDF 파일 업로드 및 OCR 처리 (결과를 JSON으로 반환)
    """
    # 프론트에서 넘어온 값('paddle', 'pytesseract', 'easyocr')을 
    # pdfocr.py에 전달하기 위해 매핑
    engine_mapping = {
        "paddle": "paddleocr",
        "pytesseract": "pytesseract",
        "easyocr": "easyocr"
    }
    engine_name = engine_mapping.get(ocr_engine, 'paddleocr') # 기본값은 paddleocr

    results = {}
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            results[file.filename] = "ERROR: PDF 파일만 업로드 가능합니다."
            continue
        try:
            pdf_bytes = await file.read()
            # pdf_to_text_with_ocr 함수는 pdfocr.py에 정의되어 있습니다.
            text = await run_in_threadpool(pdf_to_text_with_ocr, pdf_bytes, engine_name) 
            results[file.filename] = text
        except Exception as e:
            results[file.filename] = f"ERROR: 처리 중 오류 발생 - {str(e)}"

    return results # JSON으로 반환