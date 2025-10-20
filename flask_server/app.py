from flask import Flask, jsonify, request, send_from_directory
import pandas as pd
import numpy as np
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

app = Flask(__name__, static_folder='./static')

# React 정적 파일 서빙
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

# 자재 정보
materials = {
    'ConcreteBrick': ('ConcreteBrick_190x90x57mm.csv', ['서울', '인천', '부산', '대구', '대전', '광주', '울산', '수원', '춘천']),
    'GypsumFlatBoard': ('GypsumFlatBoard_9.5Tx900x1800.csv', ['서울', '인천', '부산', '대구', '대전', '광주', '강원']),
    'MDF': ('MDF_9T×1,200×2,440.csv', ['서울', '부산', '대구', '광주', '대전', '제주']),
    'ReadyMixedConcrete': ('ReadyMixedConcrete_2518,120.csv', ['서울', '인천', '부산', '대구', '광주', '대전', '원주']),
    'RoundSteelBars': ('RoundSteelBars.csv', ['서울', '인천', '부산', '대구', '대전', '광주', '전주']),
}

# 데이터 정제 함수
def clean_data(df, keep_columns=None):
    for column in df.columns:
        if keep_columns and column in keep_columns:
            continue
        df[column] = df[column].astype(str).str.replace(',', '', regex=False)
        df[column] = df[column].replace('-', np.nan)
        df[column] = pd.to_numeric(df[column], errors='coerce')
    if keep_columns:
        df = df.dropna(subset=[col for col in df.columns if col not in keep_columns])
    else:
        df = df.dropna()
    return df

# 자재 데이터 로드
def load_item_data(file_name, regions):
    file_path = os.path.join('./Item', file_name)
    df = pd.read_csv(file_path, encoding='cp949')
    df['Date'] = pd.to_datetime(df['년/월'], format='%Y년 %m월')
    df = df[['Date'] + regions]
    df.set_index('Date', inplace=True)
    for column in regions:
        df[column] = df[column].astype(str).str.replace(',', '', regex=False)
        df[column] = pd.to_numeric(df[column], errors='coerce')
    df.dropna(inplace=True)
    return df

# 검증 데이터 로드
def load_validation_data(file_name, new_col_name):
    file_path = os.path.join('./Validation', file_name)
    df = pd.read_csv(file_path, encoding='cp949')
    df['Date'] = pd.to_datetime(df['년/월'], format='%Y년 %m월')
    df = df[['Date', df.columns[1]]].rename(columns={df.columns[1]: new_col_name})
    df.set_index('Date', inplace=True)
    return clean_data(df)

# LSTM 데이터 생성
def create_lstm_data(X, y, time_steps=5):
    X_lstm, y_lstm = [], []
    for i in range(len(X) - time_steps):
        X_lstm.append(X[i:i + time_steps])
        y_lstm.append(y[i + time_steps])
    return np.array(X_lstm), np.array(y_lstm)

# API: 자재 목록
@app.route('/api/materials', methods=['GET'])
def get_materials():
    return jsonify(materials)

# API: 가격 예측
@app.route('/api/predict', methods=['POST'])
def predict_price():
    try:
        data = request.json
        material = data.get('material')
        region = data.get('region')

        if not material or not region:
            return jsonify({"error": "Material and region must be provided"}), 400

        if material not in materials or region not in materials[material][1]:
            return jsonify({"error": "Invalid material or region"}), 400

        file_name, regions = materials[material]
        df_material = load_item_data(file_name, regions)

        # Validation 데이터 로드 및 병합
        cpi = load_validation_data('ConsumerPriceIndex.csv', 'CPI')
        diesel = load_validation_data('Diesel_0.001%S.csv', 'Diesel_Price')
        exchange_rate = load_validation_data('ExchangeRate.csv', 'Exchange_Rate')
        interest_rate = load_validation_data('InterestRate.csv', 'Interest_Rate')

        df_combined = df_material.merge(cpi, how='inner', left_index=True, right_index=True)
        df_combined = df_combined.merge(diesel, how='inner', left_index=True, right_index=True)
        df_combined = df_combined.merge(exchange_rate, how='inner', left_index=True, right_index=True)
        df_combined = df_combined.merge(interest_rate, how='inner', left_index=True, right_index=True)

        # Feature Engineering
        df_combined['CPI_Rolling_Mean'] = df_combined['CPI'].rolling(window=3).mean()
        df_combined['Diesel_Price_Diff'] = df_combined['Diesel_Price'].diff()
        df_combined['Month'] = df_combined.index.month
        df_combined['Quarter'] = df_combined.index.quarter
        df_combined.dropna(inplace=True)

        X = df_combined.drop(columns=[region])
        y = df_combined[region]

        # 데이터 스케일링
        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1)).flatten()

        time_steps = 5
        X_lstm, y_lstm = create_lstm_data(X_scaled, y_scaled)

        # LSTM 모델 생성 및 학습
        model = Sequential([
            Input(shape=(X_lstm.shape[1], X_lstm.shape[2])),
            LSTM(100, activation='relu', return_sequences=True),
            Dropout(0.25),
            LSTM(50, activation='relu'),
            Dropout(0.25),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
        early_stopping = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
        model.fit(X_lstm, y_lstm, epochs=100, batch_size=8, callbacks=[early_stopping], verbose=0)

        # 미래 데이터 예측
        future_steps = 72
        future_predictions = []
        current_input = X_lstm[-1].reshape(1, X_lstm.shape[1], X_lstm.shape[2])

        for _ in range(future_steps):
            prediction_scaled = model.predict(current_input)
            prediction = scaler_y.inverse_transform(prediction_scaled)[0][0]
            future_predictions.append(prediction)
            new_feature_input = current_input[:, -1:, :].copy()
            new_feature_input += np.random.uniform(-0.01, 0.01, new_feature_input.shape)  # 변동성 추가
            new_feature_input[0, 0, -1] = prediction_scaled[0][0]
            current_input = np.concatenate([current_input[:, 1:, :], new_feature_input], axis=1)

        # 미래 날짜 생성
        future_dates = pd.date_range(start="2025-01-01", periods=future_steps, freq='MS')

        # 결과 반환
        results = [{"date": date.strftime("%Y-%m-%d"), "predicted_price": float(price)}
                   for date, price in zip(future_dates, future_predictions)]
        return jsonify({"predictions": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
