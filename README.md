# AI 기반 원자재 가격 예측 프로젝트

이 프로젝트는 AI를 활용하여 주요 건설 원자재의 미래 가격을 예측하는 웹 애플리케이션입니다. 사용자는 원하는 자재와 지역을 선택하여 향후 6년간의 가격 예측 추세를 확인할 수 있습니다.

## 주요 기능

- **원자재 및 지역 선택**: 다양한 건설 원자재와 관련 지역을 선택하여 가격 예측을 요청할 수 있습니다.
- **AI 가격 예측**: LSTM (Long Short-Term Memory) 모델을 사용하여 과거 데이터와 경제 지표(소비자 물가 지수, 유가, 환율, 금리)를 기반으로 미래 가격을 예측합니다.
- **시각화**: 예측된 가격 추세를 그래프로 시각화하여 사용자가 쉽게 이해할 수 있도록 제공합니다.

## 기술 스택

- **프론트엔드**: React, ApexCharts, Axios
- **백엔드**: Flask, TensorFlow, Keras, scikit-learn, Pandas
- **데이터베이스**: CSV 파일 형태로 프로젝트에 포함

## 프로젝트 구조

```
AI_flask_app-main/
├── flask_server/         # Flask 백엔드 서버
│   ├── Item/             # 원자재 가격 데이터 (CSV)
│   ├── Validation/       # 경제 지표 데이터 (CSV)
│   ├── static/           # React 빌드 파일
│   └── app.py            # Flask 애플리케이션
├── react_client/         # React 프론트엔드
│   ├── public/
│   └── src/
│       ├── components/   # React 컴포넌트
│       └── App.js        # 메인 애플리케이션 컴포넌트
└── README.md
```

## 설치 및 실행 방법

### 1. 백엔드 서버 실행

```bash
# 1. flask_server 디렉토리로 이동
cd flask_server

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 필요한 패키지 설치
pip install -r ../requirements.txt

# 4. Flask 서버 실행
flask run
```

### 2. 프론트엔드 실행

```bash
# 1. react_client 디렉토리로 이동
cd react_client

# 2. 필요한 패키지 설치
npm install

# 3. React 애플리케이션 실행
npm start
```

## API 엔드포인트

- `GET /api/materials`: 사용 가능한 모든 원자재와 지역 목록을 반환합니다.
- `POST /api/predict`: 특정 원자재와 지역에 대한 가격 예측 결과를 반환합니다.
  - **Request Body**: `{ "material": "...", "region": "..." }`
  - **Response Body**: `{ "predictions": [{"date": "...", "predicted_price": ...}] }`
