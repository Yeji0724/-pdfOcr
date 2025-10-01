import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState({});
  const [resultFiles, setResultFiles] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [ocrEngine, setOcrEngine] = useState('paddle');
  const [loading, setLoading] = useState(false);
  const textContentRef = useRef(null);

  // 스크롤을 맨 위로 초기화
  useEffect(() => {
    if (textContentRef.current) {
      textContentRef.current.scrollTop = 0;
    }
  }, [currentIndex]);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  // 파일에서 텍스트 추출
  const handleExtract = async () => {
    if (files.length === 0) {
      alert('파일을 선택해주세요!');
      return;
    }
    setLoading(true);
    setResults({});
    setResultFiles([]);
    setCurrentIndex(0);

    const formData = new FormData();
    for (let file of files) {
      formData.append('files', file);
    }
    formData.append('ocr_engine', ocrEngine);

    try {
      // 🚨 포트 번호를 8000으로 수정했습니다.
      const response = await fetch('http://localhost:8000/extract', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setResults(data);
      setResultFiles(Object.keys(data));
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  // 이전 파일로 이동
  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  // 다음 파일로 이동
  const handleNext = () => {
    if (currentIndex < resultFiles.length - 1) setCurrentIndex(currentIndex + 1);
  };

  // 파일명 클릭 시 해당 결과로 이동
  const handleFileClick = (fileName) => {
    const index = resultFiles.indexOf(fileName);
    if (index !== -1) setCurrentIndex(index);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>PDF 텍스트 추출기</h1>
        {/* 드롭박스에서 OCR 엔진 선택 (현재는 PaddleOCR만 있지만, 백엔드 로직은 준비되어 있음) */}
        <select value={ocrEngine} onChange={(e) => setOcrEngine(e.target.value)}>
          <option value="paddle">PaddleOCR</option>
          <option value="pytesseract">PyTesseract</option>
          <option value="easyocr">EasyOCR</option>
        </select>
        <input type="file" multiple accept=".pdf" onChange={handleFileChange} />
        {files.length > 0 && (
          <div className="file-list">
            <h4>선택한 파일들:</h4>
            <ul>
              {Array.from(files).map((file, idx) => (
                <li
                  key={idx}
                  onClick={() => resultFiles.includes(file.name) && handleFileClick(file.name)}
                  style={{
                    cursor: resultFiles.includes(file.name) ? 'pointer' : 'default',
                    color: resultFiles.includes(file.name) ? '#61dafb' : 'white',
                    textDecoration: resultFiles.includes(file.name) ? 'underline' : 'none',
                  }}
                >
                  {file.name}
                </li>
              ))}
            </ul>
          </div>
        )}
        <button onClick={handleExtract} disabled={loading}>
          {loading ? '추출 중...' : '텍스트 추출'}
        </button>
      </header>
      {resultFiles.length > 0 && (
        <div className="navigation">
          <button onClick={handlePrev} disabled={currentIndex === 0}>이전</button>
          <span>{currentIndex + 1} / {resultFiles.length}</span>
          <button onClick={handleNext} disabled={currentIndex === resultFiles.length - 1}>다음</button>
        </div>
      )}
      <div className="results">
        {resultFiles.length > 0 && (
          <div className="result-box">
            <h3 className="filename">{resultFiles[currentIndex]}</h3>
            <pre ref={textContentRef} className="text-content">
              {results[resultFiles[currentIndex]]}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;