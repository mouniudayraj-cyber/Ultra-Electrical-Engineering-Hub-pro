# 🤖 GOOGLE GEMINI INTEGRATION

## Quant Trading Intelligence Engine

Production-ready integration of Google Gemini AI for institutional market analysis.

---

## 📦 What's Included

### 1. **master_prompt.txt**
The core system prompt that makes Gemini act as a trading analysis engine.

✅ Prevents hallucinations
✅ Enforces JSON output
✅ Multi-timeframe psychology analysis
✅ Risk-aware signal generation

### 2. **input_schema.json**
Structured data format for market information.

Includes:
- OHLCV data (1m to 1D)
- Options chain (OI, PCR, IV)
- Volume metrics
- Sentiment scores
- Liquidity data

### 3. **gemini_api_client.py**
Production-ready Python client for Gemini integration.

Features:
- Single & batch analysis
- Streaming responses
- Error handling
- JSON parsing
- Display formatting

---

## 🚀 Quick Start

### 1. Get API Key
```bash
# Visit: https://ai.google.dev/
# Create API key from Google AI Studio
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Client
```python
from gemini_api_client import GeminiTradingEngine

engine = GeminiTradingEngine(api_key="YOUR_API_KEY")
```

### 4. Analyze Market
```python
market_data = {
    "symbol": "NIFTY50",
    "timestamp": "2024-01-15T14:30:00Z",
    "timeframes": {
        "5m": {"current_price": 50030, "atr_14": 120, "rsi_14": 65},
        "15m": {"current_price": 50030, "atr_14": 150, "rsi_14": 58},
        "1h": {"current_price": 50030, "atr_14": 200, "rsi_14": 55}
    },
    "derivatives_data": {"put_call_ratio": 1.15, "implied_volatility": 18.5}
}

result = engine.analyze_market(market_data)
print(engine.format_signal_for_display(result))
```

---

## 📊 Output Format

```json
{
  "analysis_timestamp": "2024-01-15T14:30:00Z",
  "symbol": "NIFTY50",
  "market_state": "TRENDING UP",
  "timeframes": {
    "LTF_5m": {
      "fear_index": 25,
      "greed_index": 70,
      "trap_probability": 35,
      "institutional_flow": 65,
      "strength": "Strong uptrend with volume confirmation"
    },
    "MTF_15m": {...},
    "HTF_1h": {...}
  },
  "signal": {
    "direction_up_probability": 67,
    "direction_down_probability": 33,
    "confidence_percent": 72,
    "expected_move_percent": "0.8 - 1.4",
    "risk_level": "MEDIUM"
  },
  "key_insights": [
    "Multi-timeframe alignment bullish",
    "Volume supporting uptrend",
    "Institutional flow positive"
  ],
  "warnings": [
    "Moderate trap probability - use tight stops"
  ],
  "recommendation": "✅ STRONG BUY - High probability with proper risk management"
}
```

---

## 🔧 Advanced Usage

### Streaming Analysis
```python
for chunk in engine.stream_analysis(market_data):
    print(chunk, end="", flush=True)
```

### Batch Analysis (Multiple Symbols)
```python
market_data_list = [data_nifty, data_bank_nifty, data_fin_nifty]
results = engine.batch_analyze(market_data_list)
```

### Custom Formatting
```python
formatted = engine.format_signal_for_display(result)
print(formatted)
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# .env file
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash
```

### Model Selection
```python
# Fast analysis (recommended for real-time)
engine = GeminiTradingEngine(api_key="key", model="gemini-2.0-flash")

# More detailed analysis
engine = GeminiTradingEngine(api_key="key", model="gemini-1.5-pro")
```

---

## 🎯 Key Features

✅ **Multi-Timeframe Analysis**
- Separate LTF (5m), MTF (15m), HTF (1h) analysis
- Alignment scoring across timeframes

✅ **Psychology Scoring**
- Fear Index (panic detection)
- Greed Index (FOMO detection)
- Trap Probability (fake breakout detection)
- Institutional Flow (smart money tracking)

✅ **Risk Management**
- Trap-based confidence reduction
- Volatility-aware risk levels
- Stop-loss & take-profit generation

✅ **Production Ready**
- Error handling
- JSON validation
- Logging
- Batch processing

---

## ❌ What This Is NOT

❌ A financial advisor
❌ A guaranteed profit system
❌ A replacement for risk management
❌ 80-90% accuracy (unrealistic)

## ✅ What This IS

✅ A probabilistic market analysis tool
✅ A decision-support system
✅ An institutional-grade signal engine
✅ A foundation for trading automation

---

## 🚨 Important Notes

1. **Always backtest** before live trading
2. **Risk management is critical** - never ignore SL/TP
3. **Gemini can hallucinate** - validate signals with other tools
4. **API costs** - monitor usage in Google AI Studio dashboard

---

## 📱 Integration with Your App

### Android App
```kotlin
// Will integrate with your Electrical Engineering Hub
// Real-time market signals on dashboard
```

### Web Dashboard
```javascript
// FastAPI backend calls Gemini
// Frontend displays signal cards
```

---

## 🔗 Next Steps

1. **Get API Key**: https://ai.google.dev/
2. **Test with sample data**: Run the example in `gemini_api_client.py`
3. **Integrate with Phase 1 data engine**: Connect to real market feeds
4. **Deploy backend**: Use FastAPI/Node.js to expose signals
5. **Build UI**: Display signals in real-time dashboard

---

**Status**: 🟢 **PRODUCTION READY**

**Version**: 1.0.0

**Last Updated**: 2024-01-15
