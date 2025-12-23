# Football Predictor FastAPI

Simple REST API for easy model predictions without complex Django logic.

## Installation

```bash
pip install -r requirements_api.txt
```

## Running the API

```bash
python fastapi_predictor.py
```

Or with uvicorn directly:
```bash
uvicorn fastapi_predictor:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at: `http://localhost:8001`

## API Endpoints

### 1. Root
```
GET /
```
Returns API information and available endpoints.

### 2. Health Check
```
GET /health
```
Check if API and models are loaded correctly.

### 3. Model Status
```
GET /models
```
Check which models are loaded and their details.

### 4. Predict (POST)
```
POST /predict
Content-Type: application/json

{
    "home_team": "Lugano",
    "away_team": "Luzern",
    "category": "Others"  # Optional
}
```

**Response:**
```json
{
    "home_team": "Lugano",
    "away_team": "Luzern",
    "prediction": "Home",
    "home_score": 2,
    "away_score": 1,
    "probabilities": {
        "Home": 0.50,
        "Draw": 0.28,
        "Away": 0.22
    },
    "confidence": 0.50,
    "model_type": "Model2",
    "form_home": "DLLWW",
    "form_away": "WWDDL"
}
```

### 5. Predict Simple (GET)
```
GET /predict/simple?home_team=Lugano&away_team=Luzern
```

Quick GET endpoint for simple predictions.

## Example Usage

### Python
```python
import requests

response = requests.post("http://localhost:8001/predict", json={
    "home_team": "Lugano",
    "away_team": "Luzern"
})

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Probabilities: {result['probabilities']}")
```

### cURL
```bash
curl -X POST "http://localhost:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{"home_team": "Lugano", "away_team": "Luzern"}'
```

### JavaScript
```javascript
fetch('http://localhost:8001/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        home_team: 'Lugano',
        away_team: 'Luzern'
    })
})
.then(res => res.json())
.then(data => console.log(data));
```

## Benefits

- ✅ Simple REST API - no complex Django logic
- ✅ Easy to use from any language
- ✅ Fast and lightweight
- ✅ Automatic model loading
- ✅ Includes form features
- ✅ Returns probabilities and confidence
- ✅ Can run alongside Django or standalone

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

