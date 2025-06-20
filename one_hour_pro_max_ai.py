import pandas as pd
import numpy as np
import requests
import shap
import datetime
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.utils import resample
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import StandardScaler

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

# === CONFIG ===
API_KEYS = [
    '54a7479bdf2040d3a35d6b3ae6457f9d',
    'd162b35754ca4c54a13ebe7abecab4e0',
    'a7266b2503fd497496d47527a7e63b5d',
    '54a7479bdf2040d3a35d6b3ae6457f9d',
    '09c09d58ed5e4cf4afd9a9cac8e09b5d',
    'df00920c02c54a59a426948a47095543'
]
INTERVAL = '1h'
SYMBOLS = ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD', 'EUR/GBP']
MULTIPLIER = 100
api_usage_index = 0

def get_next_api_key():
    global api_usage_index
    key = API_KEYS[api_usage_index % len(API_KEYS)]
    api_usage_index += 1
    return key

def fetch_data(symbol):
    try:
        api_key = get_next_api_key()
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&outputsize=300&apikey={api_key}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "values" not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data["values"])
        df = df.astype({'open': float, 'high': float, 'low': float, 'close': float})
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df.sort_values('datetime')
    except Exception as e:
        print(f"[ERROR fetching {symbol}] - {e}")
        return pd.DataFrame()

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / (avg_loss + 1e-6)
    return 100 - (100 / (1 + rs))

def compute_macd(df):
    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return macd - signal

def compute_adx(df, period=14):
    high, low, close = df['high'], df['low'], df['close']
    plus_dm = np.where((high.diff() > low.diff()) & (high.diff() > 0), high.diff(), 0)
    minus_dm = np.where((low.diff() > high.diff()) & (low.diff() > 0), low.diff(), 0)
    tr = np.maximum.reduce([high - low, abs(high - close.shift()), abs(low - close.shift())])
    atr = pd.Series(tr).rolling(window=period).mean()
    plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / (atr + 1e-6)
    minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / (atr + 1e-6)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-6)) * 100
    return pd.Series(dx).rolling(window=period).mean()

def add_features(df):
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ema10'] = df['close'].ewm(span=10).mean()
    df['rsi14'] = compute_rsi(df['close'])
    df['momentum'] = df['close'] - df['close'].shift(4)
    df['macd'] = compute_macd(df)
    df['adx'] = compute_adx(df)
    df['bb_upper'] = df['close'].rolling(20).mean() + 2 * df['close'].rolling(20).std()
    df['bb_lower'] = df['close'].rolling(20).mean() - 2 * df['close'].rolling(20).std()
    df['volatility'] = df['high'] - df['low']
    df['target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    return df.dropna()

def train_ensemble_model(df):
    features = ['ma5', 'ma10', 'ema10', 'rsi14', 'momentum', 'macd', 'adx', 'bb_upper', 'bb_lower', 'volatility']
    df_1 = df[df['target'] == 1]
    df_0 = df[df['target'] == 0]
    min_len = min(len(df_1), len(df_0))
    df_bal = pd.concat([
        resample(df_1, replace=True, n_samples=min_len, random_state=42),
        resample(df_0, replace=True, n_samples=min_len, random_state=42)
    ]).sample(frac=1).reset_index(drop=True)

    X = df_bal[features]
    y = df_bal['target']

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features)

    tscv = TimeSeriesSplit(n_splits=3)
    acc_scores = []

    xgb = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss', verbosity=0)
    lgbm = LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, verbosity=-1)
    cat = CatBoostClassifier(iterations=100, depth=4, learning_rate=0.05, verbose=0)

    for train_idx, test_idx in tscv.split(X_scaled):
        X_train, X_test = X_scaled.iloc[train_idx], X_scaled.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        ensemble = VotingClassifier(estimators=[('xgb', xgb), ('lgbm', lgbm), ('cat', cat)], voting='soft')
        ensemble.fit(X_train, y_train)
        preds = ensemble.predict(X_test)
        acc_scores.append(accuracy_score(y_test, preds))

    final_ensemble = VotingClassifier(estimators=[('xgb', xgb), ('lgbm', lgbm), ('cat', cat)], voting='soft')
    final_ensemble.fit(X_scaled, y)
    return final_ensemble, np.mean(acc_scores), scaler
def get_feature_importance(model, features):
    importance_dict = {}
    for name, estimator in model.named_estimators_.items():
        try:
            importance = estimator.feature_importances_
            importance_dict[name] = pd.DataFrame({
                'Feature': features,
                'Importance': importance
            }).sort_values(by='Importance', ascending=False).head(3)
        except:
            continue
    return importance_dict


def predict(df, model, scaler, symbol, importance_info=None):
    features = ['ma5', 'ma10', 'ema10', 'rsi14', 'momentum', 'macd', 'adx', 'bb_upper', 'bb_lower', 'volatility']
    last = df.iloc[-1]
    X_pred = df[features].iloc[[-1]]
    X_pred_scaled = pd.DataFrame(scaler.transform(X_pred), columns=features)
    proba = model.predict_proba(X_pred_scaled)[0]
    signal = "BUY 📈" if proba[1] > 0.5 else "SELL 🔉"

    # Confidence rule-based check
    confidence = sum([
        last['ema10'] > last['ma10'],
        last['momentum'] > 0,
        last['macd'] > 0,
        last['adx'] > 20,
        last['close'] < last['bb_lower'] if proba[1] > 0.5 else last['close'] > last['bb_upper']
    ])
    conf_label = "✅ Strong" if confidence >= 4 else "⚠️ Weak"
    price = round(last['close'], 4)
    tp = price + 0.0020 if signal == "BUY 📈" else price - 0.0020
    sl = price - 0.0015 if signal == "BUY 📈" else price + 0.0015

    # === Feature Importance (Explainability) ===
    importances = np.mean([
        model.named_estimators_['xgb'].feature_importances_,
        model.named_estimators_['lgbm'].feature_importances_,
        model.named_estimators_['cat'].get_feature_importance()
    ], axis=0)

    importance_df = pd.DataFrame({'Feature': features, 'Importance': importances})
    top_features = ', '.join(importance_df.sort_values(by='Importance', ascending=False).head(3)['Feature'])

    return {
        "Symbol": symbol,
        "Signal": signal,
        "Prob BUY": round(proba[1], 2),
        "RSI": round(last['rsi14'], 1),
        "Confidence": conf_label,
        "Price x100": round(price * MULTIPLIER, 2),
        "Plan": f"{price} / TP: {round(tp, 4)} / SL: {round(sl, 4)}",
        "Top Features": top_features
    }

def run_signal_engine():
    results = []
    for symbol in SYMBOLS:
        print(f"🔄 Fetching data for {symbol}...")
        df = fetch_data(symbol)

        if df.empty or len(df) < 100:
            print(f"⛔ Skipped {symbol}: Not enough data.")
            continue

        df = add_features(df)
        model, acc, scaler = train_ensemble_model(df)
        importance_info = get_feature_importance(model, ['ma5', 'ma10', 'ema10', 'rsi14', 'momentum', 'macd', 'adx', 'bb_upper', 'bb_lower', 'volatility'])


        if model is None or scaler is None:
            print(f"⚠️ Skipped {symbol}: Model training failed.")
            continue

        if acc <= 0.7:
            print(f"⚠️ Skipped {symbol}: Low accuracy ({acc:.2f}).")
            continue

        results.append(predict(df, model, scaler, symbol))



    if not results:
        print("❌ No signals generated.")
    return pd.DataFrame(results)

# === RUN ===
if __name__ == "__main__":
    output = run_signal_engine()
    if not output.empty:
        print(output.to_markdown(index=False))
    else:
        print("⚠️ No signals generated. Retry later.")

        print("⚠️ No signals generated. Retry later.")
