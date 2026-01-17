#!/usr/bin/env python3

import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, List
import yfinance as yf
import pandas as pd


class MarketRegimeLSTM(nn.Module):
    def __init__(self, input_size: int = 2, hidden_size: int = 64, num_layers: int = 1, num_classes: int = 3, dropout: float = 0.2):
        super(MarketRegimeLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out


def generate_synthetic_data(n_sequences: int = 1000, sequence_length: int = 30) -> Tuple[np.ndarray, np.ndarray]:
    X = []
    y = []
    
    np.random.seed(42)
    
    for i in range(n_sequences):
        base_freq = np.random.uniform(0.05, 0.2)
        amplitude = np.random.uniform(0.01, 0.05)
        noise_level = np.random.uniform(0.001, 0.01)
        
        regime_type = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
        
        if regime_type == 0:
            trend = np.linspace(0, amplitude * 10, sequence_length)
            sine_wave = np.sin(2 * np.pi * base_freq * np.arange(sequence_length)) * amplitude
            returns = trend + sine_wave + np.random.normal(0, noise_level, sequence_length)
            volume_factor = np.random.uniform(0.8, 1.2, sequence_length)
        elif regime_type == 1:
            trend = np.zeros(sequence_length)
            sine_wave = np.sin(2 * np.pi * base_freq * np.arange(sequence_length)) * amplitude * 2
            returns = trend + sine_wave + np.random.normal(0, noise_level * 1.5, sequence_length)
            volume_factor = np.random.uniform(1.0, 1.5, sequence_length)
        else:
            trend = np.linspace(0, -amplitude * 15, sequence_length)
            sine_wave = np.sin(2 * np.pi * base_freq * np.arange(sequence_length)) * amplitude
            returns = trend + sine_wave + np.random.normal(0, noise_level * 2, sequence_length)
            volume_factor = np.random.uniform(1.2, 2.0, sequence_length)
        
        returns = returns.reshape(-1, 1)
        volumes = volume_factor.reshape(-1, 1)
        sequence = np.concatenate([returns, volumes], axis=1)
        
        X.append(sequence)
        y.append(regime_type)
    
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


def train_mock_model():
    print("Generating synthetic training data...")
    X, y = generate_synthetic_data(n_sequences=1000, sequence_length=30)
    
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.LongTensor(y)
    
    train_size = int(0.8 * len(X))
    X_train, X_val = X_tensor[:train_size], X_tensor[train_size:]
    y_train, y_val = y_tensor[:train_size], y_tensor[train_size:]
    
    model = MarketRegimeLSTM(input_size=2, hidden_size=64, num_layers=1, num_classes=3, dropout=0.2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    n_epochs = 10
    batch_size = 32
    
    print(f"Training model for {n_epochs} epochs...")
    
    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        
        for i in range(0, len(X_train), batch_size):
            batch_X = X_train[i:i+batch_size]
            batch_y = y_train[i:i+batch_size]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            n_batches += 1
        
        avg_loss = epoch_loss / n_batches if n_batches > 0 else 0.0
        
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs, y_val).item()
            _, predicted = torch.max(val_outputs.data, 1)
            val_accuracy = (predicted == y_val).sum().item() / len(y_val)
        
        print(f"Epoch {epoch+1}/{n_epochs} - Loss: {avg_loss:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_accuracy:.2%}")
    
    os.makedirs("models", exist_ok=True)
    model_path = "models/regime_model.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")


def predict_regime(ticker: str = "SPY") -> dict:
    model_path = "models/regime_model.pth"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}. Please run train_mock_model() first.")
    
    print(f"Fetching data for {ticker}...")
    stock = yf.Ticker(ticker)
    hist = stock.history(period="60d")
    
    if hist.empty:
        raise ValueError(f"No data available for ticker {ticker}")
    
    hist = hist.sort_index()
    hist["Returns"] = hist["Close"].pct_change().fillna(0)
    hist["Volume_Norm"] = hist["Volume"] / hist["Volume"].rolling(window=20).mean()
    hist["Volume_Norm"] = hist["Volume_Norm"].fillna(1.0)
    
    returns = hist["Returns"].values[-30:]
    volumes = hist["Volume_Norm"].values[-30:]
    
    if len(returns) < 30:
        raise ValueError(f"Insufficient data for {ticker}. Need 30 days, got {len(returns)}")
    
    returns_mean = np.mean(returns)
    returns_std = np.std(returns) if np.std(returns) > 0 else 1.0
    returns_norm = (returns - returns_mean) / returns_std
    
    volumes_mean = np.mean(volumes)
    volumes_std = np.std(volumes) if np.std(volumes) > 0 else 1.0
    volumes_norm = (volumes - volumes_mean) / volumes_std
    
    sequence = np.column_stack([returns_norm, volumes_norm]).astype(np.float32)
    sequence = sequence.reshape(1, 30, 2)
    
    model = MarketRegimeLSTM(input_size=2, hidden_size=64, num_layers=1, num_classes=3, dropout=0.2)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    
    with torch.no_grad():
        input_tensor = torch.FloatTensor(sequence)
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)
        probabilities = probs[0].numpy()
    
    regime_labels = ["Bullish", "Choppy", "Bearish"]
    predicted_class = int(np.argmax(probabilities))
    
    result = {
        "regime": regime_labels[predicted_class],
        "probabilities": {
            "bullish": float(probabilities[0]),
            "choppy": float(probabilities[1]),
            "bearish": float(probabilities[2])
        },
        "crash_probability": float(probabilities[2]),
        "safety_score": float(probabilities[0] * 100)
    }
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train_mock_model()
    else:
        try:
            result = predict_regime("SPY")
            print(f"\nMarket Regime Prediction for SPY:")
            print(f"Regime: {result['regime']}")
            print(f"Bullish: {result['probabilities']['bullish']:.2%}")
            print(f"Choppy: {result['probabilities']['choppy']:.2%}")
            print(f"Bearish: {result['probabilities']['bearish']:.2%}")
            print(f"Crash Probability: {result['crash_probability']:.2%}")
            print(f"Safety Score: {result['safety_score']:.1f}%")
        except FileNotFoundError:
            print("Model not found. Training model first...")
            train_mock_model()
            result = predict_regime("SPY")
            print(f"\nMarket Regime Prediction for SPY:")
            print(f"Regime: {result['regime']}")
            print(f"Crash Probability: {result['crash_probability']:.2%}")
            print(f"Safety Score: {result['safety_score']:.1f}%")

