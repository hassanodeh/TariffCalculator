# Port Tariff Calculator

A solution for computing port tariffs for vessels calling at South African ports (Durban, Saldanha Bay, Richard’s Bay).  
Combines Retrieval-Augmented Generation (RAG) with Google Gemini AI and semantic search for precise, explainable fee calculations.

---

## Features

- **Seven Fee Categories**  
  Light Dues · Port Dues · VTS Charges · Pilotage · Towage · Berthing Services · Running-of-Vessel-Lines

- **Kits used**  
  - **Google Gemini** extracts vessel parameters and formulae  
  - **Sentence-transformer embeddings** pinpoint the exact tariff rules in the Markdown

- **For testing purposes there is:**  
  - **CLI** (`calculate_tariffs.py`) for one-off or batch runs test run.
  - **REST API** (`api/app.py`) for integration with other systems.

---

## 📋 Prerequisites

- **Python 3.8+**  
- **Environment variables:**  
  - `GEMINI_API_KEY` (Google Gemini)  
- **Dependencies:** install with `pip install -r requirements.txt`

---

## 🚀 Quick Start

1. **Clone & Install**  
   ```bash
   git clone https://github.com/your-username/port-tariff-calculator.git
   cd port-tariff-calculator
   pip install -r requirements.txt


### 2. API Keys Setup

Update the API keys in the relevant files:
- `calculate_tariffs.py`: Update  `GEMINI_API_KEY`
- `api/app.py`: Update the same API key

### 3. Basic Usage

```bash
# Calculate tariffs for default test vessel (SUDESTADA)
python calculate_tariffs.py

# Use custom vessel data
python calculate_tariffs.py --vessel-file container_ship.json --port "Richard's Bay"

```

## 📊 Command Line Usage


### Vessel Data Format

Create a JSON file with your vessel information:

```json
{
  "name": "YOUR_VESSEL_NAME",
  "gross_tonnage": 51300,
  "dead_weight_tonnage": 93274,
  "net_tonnage": 31192,
  "total_length": 229.2,
  "operations": 2,
  "vessel_type": "Bulk Carrier",
  "flag": "Malta"
}
```


## 🌐 API Usage

### Starting the API Server

```bash
# Start the Flask API server
cd api
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Calculate Tariffs
```bash
POST /calculate-tariffs
Content-Type: application/json

{
  "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Durban: SUDESTADA, Bulk Carrier, 51,300 GT",
  "vessel_info": {
    "name": "SUDESTADA",
    "gross_tonnage": 51300,
    "dead_weight_tonnage": 93274,
    "net_tonnage": 31192,
    "total_length": 229.2,
    "operations": 2,
    "vessel_type": "Bulk Carrier",
    "flag": "Malta"
  },
  "port": "Durban"
}
```

#### Get Supported Ports
```bash
GET /ports
```

#### Get Example Request
```bash
GET /example
```

### API Response Format

```json
{
  "status": "success",
  "vessel_info": {
    "name": "SUDESTADA",
    "gross_tonnage": 51300,
    "port": "Durban"
  },
  "tariffs": {
    "Light Dues": {
      "amount": 60022.44,
      "currency": "ZAR",
      "formatted": "R 60,022.44"
    },
    "Port Dues": {
      "amount": 187897.58,
      "currency": "ZAR", 
      "formatted": "R 187,897.58"
    }
  },
  "total": {
    "amount": 309104.17,
    "currency": "ZAR",
    "formatted": "R 309,104.17"
  },
  "summary": {
    "success_rate": 100.0,
    "successful_calculations": 7,
    "total_calculations": 7
  }
}
```

### API Usage Examples

#### Using cURL

```bash
# Health check
curl http://localhost:5000/health

# Calculate tariffs
curl -X POST http://localhost:5000/calculate-tariffs \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Durban: SUDESTADA, Bulk Carrier, 51,300 GT",
    "vessel_info": {
      "name": "SUDESTADA",
      "gross_tonnage": 51300,
      "vessel_type": "Bulk Carrier"
    },
    "port": "Durban"
  }'

# Get supported ports
curl http://localhost:5000/ports

# Get example request format
curl http://localhost:5000/example
```

#### Using Python requests

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/calculate-tariffs"

# Request data
data = {
    "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Durban: SUDESTADA, Bulk Carrier, 51,300 GT",
    "vessel_info": {
        "name": "SUDESTADA",
        "gross_tonnage": 51300,
        "dead_weight_tonnage": 93274,
        "net_tonnage": 31192,
        "total_length": 229.2,
        "operations": 2,
        "vessel_type": "Bulk Carrier",
        "flag": "Malta"
    },
    "port": "Durban"
}

# Make request
response = requests.post(url, json=data)
result = response.json()

# Print results
print(f"Total Tariffs: {result['total']['formatted']}")
for tariff_name, tariff_data in result['tariffs'].items():
    print(f"{tariff_name}: {tariff_data['formatted']}")
```

#### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const calculateTariffs = async () => {
  try {
    const response = await axios.post('http://localhost:5000/calculate-tariffs', {
      query: "Calculate the different tariffs payable by the following vessel berthing at the port of Durban: SUDESTADA, Bulk Carrier, 51,300 GT",
      vessel_info: {
        name: "SUDESTADA",
        gross_tonnage: 51300,
        vessel_type: "Bulk Carrier"
      },
      port: "Durban"
    });
    
    console.log('Total Tariffs:', response.data.total.formatted);
    Object.entries(response.data.tariffs).forEach(([name, data]) => {
      console.log(`${name}: ${data.formatted}`);
    });
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
};

calculateTariffs();
```

## 📁 Project Structure

```
port-tariff-calculator/
├── src/                          # Core calculation modules
│   ├── __init__.py
│   ├── parser.py                 # PDF parsing into a markdown
│   ├── section_rag_calculator.py # Main calculation engine
│   ├── section_rag_retriever.py  # Semantic section retrieval
│   └── PortTariff.pdf           # Source tariff document
├── api/                          # Flask API application
│   └── app.py                   # API server with endpoints
├── calculate_tariffs.py          # Main CLI script
├── requirements.txt              # Python dependencies
└── README.md                    # This file
```






