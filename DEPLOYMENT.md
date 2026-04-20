# Deployment Guide

This guide covers deploying the RAG System to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Deployments](#cloud-deployments)
5. [Security Considerations](#security-considerations)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring](#monitoring)

## Prerequisites

### System Requirements

**Minimum:**
- 4 CPU cores
- 8GB RAM
- 20GB disk space
- Docker 20.10+
- Docker Compose 2.0+

**Recommended:**
- 8+ CPU cores
- 16GB+ RAM
- 50GB+ SSD storage
- GPU (optional, for faster inference)

### Network Requirements

- Ports 8000 (FastAPI), 8501 (Streamlit), 6333 (Qdrant), 11434 (Ollama)
- HTTPS/TLS certificates for production
- Firewall rules configured

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rag-fastapi-prod
    restart: always
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - EMBEDDING_CACHE_ENABLED=true
    env_file:
      - .env.production
    depends_on:
      - qdrant
      - ollama
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - rag-network
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  qdrant:
    image: qdrant/qdrant:latest
    container_name: rag-qdrant-prod
    restart: always
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - rag-network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  ollama:
    image: ollama/ollama:latest
    container_name: rag-ollama-prod
    restart: always
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - rag-network
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  nginx:
    image: nginx:alpine
    container_name: rag-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - fastapi
      - streamlit
    networks:
      - rag-network

volumes:
  qdrant_data:
  ollama_data:

networks:
  rag-network:
    driver: bridge
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi {
        server fastapi:8000;
    }

    upstream streamlit {
        server streamlit:8501;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API
        location /api/ {
            proxy_pass http://fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Streaming support
            proxy_buffering off;
            proxy_cache off;
        }

        # Frontend
        location / {
            proxy_pass http://streamlit;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Deploy

```bash
# Create production env file
cp .env.example .env.production
# Edit .env.production with production values

# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale fastapi=3
```

## Kubernetes Deployment

### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: rag-system
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: rag-config
  namespace: rag-system
data:
  QDRANT_HOST: "qdrant-service"
  OLLAMA_BASE_URL: "http://ollama-service:11434"
  LOG_LEVEL: "INFO"
  CHUNK_SIZE: "400"
  TOP_K: "10"
```

### Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: rag-secrets
  namespace: rag-system
type: Opaque
stringData:
  OPENAI_API_KEY: "your-key-here"
  ANTHROPIC_API_KEY: "your-key-here"
```

### Deployments

```yaml
# fastapi-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi
  namespace: rag-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: your-registry/rag-fastapi:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: rag-config
        - secretRef:
            name: rag-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Services

```yaml
# services.yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
  namespace: rag-system
spec:
  selector:
    app: fastapi
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
  namespace: rag-system
spec:
  selector:
    app: qdrant
  ports:
  - port: 6333
    targetPort: 6333
  type: ClusterIP
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rag-ingress
  namespace: rag-system
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - rag.your-domain.com
    secretName: rag-tls
  rules:
  - host: rag.your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: streamlit-service
            port:
              number: 8501
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f services.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n rag-system
kubectl get services -n rag-system

# View logs
kubectl logs -f deployment/fastapi -n rag-system
```

## Cloud Deployments

### AWS ECS

1. Create ECR repositories
2. Push Docker images
3. Create ECS cluster
4. Define task definitions
5. Create services with load balancer

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-fastapi

# Deploy
gcloud run deploy rag-fastapi \
  --image gcr.io/PROJECT_ID/rag-fastapi \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars QDRANT_HOST=qdrant-url
```

### Azure Container Instances

```bash
# Create resource group
az group create --name rag-system --location eastus

# Deploy container
az container create \
  --resource-group rag-system \
  --name rag-fastapi \
  --image your-registry/rag-fastapi:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables \
    QDRANT_HOST=qdrant-url \
    LOG_LEVEL=INFO
```

## Security Considerations

### 1. API Authentication

Add JWT authentication:

```python
# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/query")
@limiter.limit("10/minute")
async def query(request: Request, ...):
    ...
```

### 3. Input Validation

- Already implemented via Pydantic models
- Add additional sanitization for file uploads
- Validate URLs before fetching

### 4. Secrets Management

Use environment-specific secret managers:
- AWS Secrets Manager
- Google Secret Manager
- Azure Key Vault
- HashiCorp Vault

## Performance Tuning

### 1. Embedding Cache

Enable Redis for distributed caching:

```python
# app/core/config.py
REDIS_ENABLED=true
REDIS_HOST=redis
REDIS_PORT=6379
```

### 2. Connection Pooling

```python
# Increase Qdrant connection pool
qdrant_client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
    grpc_port=6334,
    prefer_grpc=True
)
```

### 3. Async Workers

```bash
# Increase Uvicorn workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 4. Database Optimization

- Enable Qdrant quantization for reduced memory
- Use HNSW index parameters tuning
- Implement batch operations

## Monitoring

### Prometheus Metrics

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram

query_counter = Counter('rag_queries_total', 'Total queries')
query_duration = Histogram('rag_query_duration_seconds', 'Query duration')
```

### Grafana Dashboard

Import dashboard JSON for:
- Query rate and latency
- Confidence score distribution
- Document ingestion rate
- Error rates
- Resource usage

### Logging

Use structured logging with ELK stack:
- Elasticsearch for storage
- Logstash for processing
- Kibana for visualization

### Alerts

Set up alerts for:
- High error rates (> 5%)
- Low confidence scores (< 0.3)
- High latency (> 10s)
- Service downtime

## Backup and Recovery

### Qdrant Backup

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/rag_documents/snapshots

# Download snapshot
curl http://localhost:6333/collections/rag_documents/snapshots/snapshot_name \
  -o backup.snapshot

# Restore
curl -X PUT http://localhost:6333/collections/rag_documents/snapshots/upload \
  -F 'snapshot=@backup.snapshot'
```

### Automated Backups

```bash
# Cron job for daily backups
0 2 * * * /path/to/backup-script.sh
```

## Troubleshooting

See README.md troubleshooting section for common issues.

## Support

For production support:
- Email: support@example.com
- Slack: #rag-system
- On-call: PagerDuty integration
