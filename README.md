# 파이썬 3.10버전을 사용하고 있습니다.
python3.10 --version     # 3.10 버전이 있는지 확인. 없다면 다운 https://www.python.org/downloads/release/python-31011/?utm_source=chatgpt.com     <- 설치경로 알아놔야함

# Back 환경 설정
cd pdfocr\back
C:\Users\4Class_14\AppData\Local\Programs\Python\Python310\python.exe -m venv venv      # 가상환경 생성 , 설치경로 직접 지정해서 생성.
venv\scripts\activate       # 가상환경 활성화

# Tesseract OCR 경로 지정
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"   # 경로는 자신의 경로에 맞게 변경  pdfocr.py 파일에 약 20번째 줄

# requirements 설치
pip install -r requirements.txt

# OCR 라이브러리 설치 (설치가 안 되었을수도 있으니 한 번 더 체크)
pip install pytesseract 
pip install easyocr
pip install paddleocr

pip install git+https://github.com/haven-jeon/PyKoSpacing.git       # pykospacing 설치

pip install fastapi #자동 설치가 안 되었을 시 설치
pip install uvicorn # uvicorn이 다른 경로를 가리키고 있을 확률이 큼. 가상환경을 만들었다면, 여기서도 uvicorn install

# Back 실행
uvicorn main:app --reload

# Front 환경 설정
cd pdfocr\front
python3.9 -m venv venv
venv\scripts\activate

# Front 실행
npm start



# PyTorch (CPU 사용)
# CUDA 버전에 맞게 설치 필요.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 버전 호환성
Python 3.9
PyMuPDF 1.24.10
Pillow 10.2.0
OpenCV 4.9.0
pytesseract 0.3.10
easyocr 1.7.1
paddleocr 2.7.0.3
torch 2.3.0 (CUDA 11.8)
pykospacing 0.5

# tensorflow (ERROR: PaddleOCR 실행 실패, PyKoSpacing 설치 오류 시 필요할 수 있음)
pip install tensorflow==2.5.3
#에러 뜨면 파이썬 버전이 너무 높아 다운그레이 시켜야할 수도 있음