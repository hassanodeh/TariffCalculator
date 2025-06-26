# Port Tariff RAG System

A production-ready **Chunked Retrieval-Augmented Generation (RAG) system** for calculating South African port tariffs with exceptional accuracy and intelligent reasoning capabilities.

## 🎯 Overview

This system revolutionizes port tariff calculations by combining advanced PDF processing, intelligent document chunking, and LLM-powered calculations. Unlike traditional hardcoded approaches, our system dynamically extracts tariff rules from official PDF documents and applies them with human-like reasoning.

### Key Features

- **🔥 Chunked RAG Architecture**: Separate vector indices for each tariff type ensure targeted, accurate retrieval
- **📄 Advanced PDF Processing**: LlamaParse integration preserves document structure and relationships  
- **🤖 Gemini LLM Integration**: Intelligent calculations with step-by-step reasoning
- **⚡ High Accuracy**: Proven 99-100% accuracy on multiple tariff types
- **🚀 Production Ready**: Complete REST API with comprehensive error handling
- **📊 Zero Hardcoded Values**: All rates and formulas extracted dynamically from PDF
- **🔧 Modular Architecture**: Clean separation of concerns for maintainability

### Supported Tariff Types

1. **Light Dues** - Navigation and lighthouse charges
2. **Port Dues** - Harbor and berth charges  
3. **VTS Dues** - Vessel Traffic Services charges
4. **Pilotage Dues** - Pilot service charges
5. **Towage Dues** - Tug assistance charges
6. **Vessel Lines Dues** - Mooring and line handling charges

## 🏗️ Architecture

```
PDF Document (PortTariff.pdf)
    ↓
LlamaParse (Structure-Aware Extraction)
    ↓
Content Chunking by Tariff Type
    ├── light_dues_chunk → Vector Index
    ├── port_dues_chunk → Vector Index  
    ├── vts_dues_chunk → Vector Index
    ├── pilotage_dues_chunk → Vector Index
    ├── towage_dues_chunk → Vector Index
    └── vessel_lines_dues_chunk → Vector Index
    ↓
RAG Retrieval (Tariff-Specific Context)
    ↓
Gemini LLM (Focused Calculation)
    ↓
Accurate Tariff Results
```

## 📊 Proven Results

**Test Vessel: SUDESTADA (GT: 51,300, Durban, 2 operations)**

| Tariff Type | Calculated | Expected | Accuracy |
|-------------|------------|----------|----------|
| Light Dues | ZAR 60,062.04 | ZAR 60,062.04 | **100.0%** |
| Port Dues | ZAR 199,371.35 | ZAR 199,549.22 | **99.9%** |
| VTS Dues | ZAR 33,345.00 | ZAR 33,315.75 | **99.9%** |
| Pilotage Dues | ZAR 47,189.94 | ZAR 47,189.94 | **100.0%** |
| Towage Dues | ZAR 147,074.38 | ZAR 147,074.38 | **100.0%** |
| Vessel Lines Dues | ZAR 22,946.76 | ZAR 19,639.50 | **83.2%** |

**Overall System Accuracy: 97.2%**

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API Keys:
  - Gemini API Key (required for LLM calculations)
  - LlamaCloud API Key (optional, for advanced PDF parsing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/port-tariff-rag-system.git
cd port-tariff-rag-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export GEMINI_API_KEY="your_gemini_api_key"
export LLAMA_CLOUD_API_KEY="your_llama_cloud_key"  # Optional
```

4. **Run the system**
```bash
python -m src.api.app
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t port-tariff-rag .
docker run -p 8000:8000 -e GEMINI_API_KEY="your_key" port-tariff-rag
```

## 📖 API Usage

### Calculate All Tariffs

```bash
curl -X POST "http://localhost:8000/api/v1/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_info": {
      "name": "SUDESTADA",
      "gross_tonnage": 51300,
      "length_overall": 229.2,
      "port": "Durban",
      "vessel_type": "bulk_carrier",
      "days_alongside": 3.39,
      "operations_count": 2
    }
  }'
```

### Calculate Specific Tariff

```bash
curl -X POST "http://localhost:8000/api/v1/calculate/pilotage_dues" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SUDESTADA",
    "gross_tonnage": 51300,
    "port": "Durban",
    "operations_count": 2
  }'
```

### View Available Endpoints

```bash
curl http://localhost:8000/docs
```

## 🔧 Configuration

The system uses environment variables for configuration:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
LLAMA_CLOUD_API_KEY=your_llama_cloud_key
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
```

## 📁 Project Structure

```
port-tariff-rag-system/
├── src/                          # Source code
│   ├── core/                     # Core business logic
│   │   ├── models.py            # Data models and schemas
│   │   ├── config.py            # Configuration management
│   │   ├── pdf_processor.py     # PDF processing and chunking
│   │   ├── rag_engine.py        # RAG engine and vector indexing
│   │   └── calculator_service.py # Main calculation service
│   ├── api/                      # REST API
│   │   ├── app.py               # Flask application
│   │   └── routes.py            # API routes and handlers
│   └── utils/                    # Utility functions
│       └── helpers.py           # Common helper functions
├── tests/                        # Test suites
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── config/                       # Configuration files
├── data/                         # Data files (PDF, etc.)
├── examples/                     # Usage examples
├── docker/                       # Docker configurations
├── deployment/                   # Deployment configurations
├── .github/workflows/           # CI/CD workflows
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
└── README.md                    # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## 🚀 Deployment

### Local Development
```bash
python -m src.api.app
```

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Using Kubernetes
kubectl apply -f deployment/k8s/
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture details
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Development Guide](docs/DEVELOPMENT.md) - Development setup and guidelines
- [Configuration Reference](docs/CONFIGURATION.md) - Configuration options

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/port-tariff-rag-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/port-tariff-rag-system/discussions)
- **Email**: support@your-org.com

## 🏆 Achievements

✅ **Zero Hardcoded Values** - All rates extracted from PDF  
✅ **Advanced PDF Processing** - LlamaParse integration  
✅ **Intelligent LLM** - Gemini-powered calculations  
✅ **Chunked Architecture** - Dedicated context per tariff  
✅ **High Accuracy** - 97%+ overall accuracy  
✅ **Production Ready** - Complete API and documentation  

---

**Built with ❤️ by the Port Tariff RAG Team**

