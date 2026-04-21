# Requirements Files Guide

This project has different requirements files for different deployment scenarios:

## Files

### `requirements.txt` (Streamlit Cloud - Demo)
- **Purpose**: Minimal dependencies for Streamlit Cloud demo deployment
- **Contains**: Only Streamlit and basic utilities
- **Used by**: Streamlit Cloud (streamlit_app.py)
- **Size**: Minimal (~2 packages)

### `requirements_full.txt` (Full System)
- **Purpose**: Complete dependencies for full RAG system
- **Contains**: All backend, LLM, vector DB, and processing dependencies
- **Used by**: Docker, local development, production deployments
- **Size**: Full (~40+ packages)

### `requirements_gradio.txt` (Gradio Interface)
- **Purpose**: Dependencies for Gradio-based interface
- **Contains**: Gradio and related packages
- **Used by**: gradio_app.py

## Usage

### For Streamlit Cloud Demo
```bash
# Already configured - just deploy to Streamlit Cloud
# Uses requirements.txt automatically
```

### For Full System (Docker)
```bash
# Dockerfile uses requirements_full.txt
docker-compose up
```

### For Local Development
```bash
# Install full dependencies
pip install -r requirements_full.txt
```

### For Gradio Interface
```bash
pip install -r requirements_gradio.txt
```

## Why Multiple Files?

1. **Streamlit Cloud Limitations**: Free tier has memory/build time limits
2. **Faster Deployments**: Demo doesn't need heavy ML libraries
3. **Flexibility**: Different interfaces need different dependencies
4. **Cost Optimization**: Minimal dependencies = faster builds = lower costs

## Deployment Matrix

| Deployment Type | Requirements File | Purpose |
|----------------|------------------|---------|
| Streamlit Cloud | `requirements.txt` | Demo/Documentation |
| Docker (Full) | `requirements_full.txt` | Production System |
| Local Dev | `requirements_full.txt` | Development |
| Gradio | `requirements_gradio.txt` | Alternative UI |

## Notes

- Streamlit Cloud automatically uses `requirements.txt`
- Docker files explicitly reference `requirements_full.txt`
- Keep `requirements.txt` minimal for Streamlit Cloud compatibility
