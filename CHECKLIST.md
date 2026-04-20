# RAG System - Deployment Checklist

Use this checklist to ensure proper setup and deployment of the RAG system.

## Pre-Deployment Checklist

### ☐ System Requirements
- [ ] Docker 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Minimum 8GB RAM available
- [ ] Minimum 20GB disk space available
- [ ] Ports 8000, 8501, 6333, 11434 available

### ☐ Configuration
- [ ] `.env` file created from `.env.example`
- [ ] API keys configured (if using external providers)
  - [ ] `OPENAI_API_KEY` (if using OpenAI)
  - [ ] `ANTHROPIC_API_KEY` (if using Anthropic)
  - [ ] `COHERE_API_KEY` (if using Cohere)
- [ ] LLM provider selected (`LLM_PROVIDER`)
- [ ] Embedding provider selected (`EMBEDDING_PROVIDER`)
- [ ] Confidence threshold configured (`CONFIDENCE_THRESHOLD`)
- [ ] Chunk size and overlap configured
- [ ] Log level set appropriately

### ☐ Directory Structure
- [ ] `data/` directory exists
- [ ] `logs/` directory exists
- [ ] `data/cache/` directory exists
- [ ] Proper permissions set (read/write)

## Deployment Checklist

### ☐ Docker Deployment
- [ ] Images built successfully
  ```bash
  docker-compose build
  ```
- [ ] Services started
  ```bash
  docker-compose up -d
  ```
- [ ] All containers running
  ```bash
  docker-compose ps
  ```
- [ ] No error logs
  ```bash
  docker-compose logs
  ```

### ☐ Service Health Checks
- [ ] Qdrant accessible
  ```bash
  curl http://localhost:6333/health
  ```
- [ ] Ollama accessible
  ```bash
  curl http://localhost:11434/api/tags
  ```
- [ ] FastAPI accessible
  ```bash
  curl http://localhost:8000/api/v1/health
  ```
- [ ] Streamlit accessible
  ```bash
  curl http://localhost:8501
  ```

### ☐ Ollama Models
- [ ] Embedding model downloaded
  ```bash
  docker exec rag-ollama ollama list | grep nomic-embed-text
  ```
- [ ] LLM model downloaded
  ```bash
  docker exec rag-ollama ollama list | grep llama3
  ```

### ☐ Qdrant Setup
- [ ] Collection created
  ```bash
  curl http://localhost:6333/collections
  ```
- [ ] Correct vector size configured
- [ ] Distance metric set to Cosine
- [ ] Payload indexes created

## Functional Testing Checklist

### ☐ Document Ingestion
- [ ] PDF upload works
  - [ ] Small PDF (<5MB)
  - [ ] Large PDF (>10MB)
  - [ ] Multi-page PDF
- [ ] Text file upload works
- [ ] URL ingestion works
- [ ] Duplicate detection works
- [ ] Metadata preserved
- [ ] Chunks created correctly

### ☐ Query Functionality
- [ ] Basic query works
- [ ] Query returns answer
- [ ] Citations included
- [ ] Confidence score present
- [ ] Query rewriting visible
- [ ] Fallback message works (for irrelevant queries)

### ☐ Anti-Hallucination Checks
- [ ] Low confidence returns fallback
- [ ] No chunks returns fallback
- [ ] Citations always present (when not fallback)
- [ ] Confidence threshold enforced
- [ ] System prompt prevents external knowledge

### ☐ Streaming
- [ ] Streaming endpoint works
- [ ] SSE events received
- [ ] Metadata sent first
- [ ] Answer chunks stream correctly
- [ ] Citations sent last

### ☐ Document Management
- [ ] List documents works
- [ ] Document count accurate
- [ ] Delete document works
- [ ] Chunks removed after deletion

### ☐ Frontend
- [ ] Streamlit loads
- [ ] File upload works
- [ ] URL ingestion works
- [ ] Chat interface functional
- [ ] Citations displayed
- [ ] Confidence bar shows
- [ ] LLM provider selection works
- [ ] Document list updates

## Performance Testing Checklist

### ☐ Latency
- [ ] Query latency <10s (p95)
- [ ] Ingestion latency acceptable
- [ ] Streaming starts quickly (<2s)

### ☐ Throughput
- [ ] Handles 10 concurrent queries
- [ ] No memory leaks over time
- [ ] CPU usage reasonable

### ☐ Resource Usage
- [ ] Memory usage <8GB
- [ ] Disk usage monitored
- [ ] No disk space issues

## Security Checklist

### ☐ Input Validation
- [ ] File type validation works
- [ ] File size limits enforced
- [ ] URL validation works
- [ ] Query length limits enforced

### ☐ Error Handling
- [ ] Errors don't expose internals
- [ ] Stack traces hidden in production
- [ ] Proper HTTP status codes
- [ ] Error messages user-friendly

### ☐ Network Security
- [ ] CORS configured appropriately
- [ ] Ports not exposed unnecessarily
- [ ] Firewall rules set (if applicable)

## Production Checklist

### ☐ Environment
- [ ] Production `.env` file created
- [ ] Secrets not in version control
- [ ] Environment variables validated
- [ ] Log level set to INFO or WARNING

### ☐ Monitoring
- [ ] Health check endpoint monitored
- [ ] Logs being collected
- [ ] Disk space monitored
- [ ] Memory usage monitored
- [ ] Error rates tracked

### ☐ Backup
- [ ] Qdrant backup strategy defined
- [ ] Backup schedule configured
- [ ] Restore procedure tested
- [ ] Data retention policy set

### ☐ Scaling
- [ ] Horizontal scaling tested (if needed)
- [ ] Load balancer configured (if needed)
- [ ] Database connection pooling configured
- [ ] Cache strategy defined

### ☐ Documentation
- [ ] README.md reviewed
- [ ] API.md accessible
- [ ] DEPLOYMENT.md followed
- [ ] Team trained on system

## Post-Deployment Checklist

### ☐ Smoke Tests
- [ ] Ingest sample document
- [ ] Run sample queries
- [ ] Verify responses accurate
- [ ] Check citations present
- [ ] Verify confidence scores

### ☐ User Acceptance
- [ ] Demo to stakeholders
- [ ] Collect initial feedback
- [ ] Document known issues
- [ ] Create issue tracker

### ☐ Monitoring Setup
- [ ] Alerts configured
- [ ] Dashboard created
- [ ] On-call rotation defined
- [ ] Incident response plan ready

### ☐ Maintenance Plan
- [ ] Update schedule defined
- [ ] Backup verification scheduled
- [ ] Performance review scheduled
- [ ] Security audit scheduled

## Troubleshooting Checklist

### ☐ If Services Won't Start
- [ ] Check Docker daemon running
- [ ] Check port conflicts
- [ ] Check disk space
- [ ] Check Docker logs
- [ ] Verify `.env` file exists

### ☐ If Queries Fail
- [ ] Check Qdrant connection
- [ ] Check Ollama connection
- [ ] Verify documents ingested
- [ ] Check logs for errors
- [ ] Verify API endpoint accessible

### ☐ If Ingestion Fails
- [ ] Check file format supported
- [ ] Check file size reasonable
- [ ] Check disk space available
- [ ] Verify Qdrant accessible
- [ ] Check embedding generation

### ☐ If Confidence Always Low
- [ ] Verify documents relevant
- [ ] Check embedding model loaded
- [ ] Verify chunk quality
- [ ] Review confidence threshold
- [ ] Check retrieval parameters

## Rollback Checklist

### ☐ If Deployment Fails
- [ ] Stop new services
  ```bash
  docker-compose down
  ```
- [ ] Restore previous version
- [ ] Verify previous version works
- [ ] Document failure reason
- [ ] Plan fix for next deployment

### ☐ If Data Corrupted
- [ ] Stop services
- [ ] Restore Qdrant from backup
- [ ] Verify data integrity
- [ ] Restart services
- [ ] Re-test functionality

## Maintenance Checklist

### ☐ Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backups running

### ☐ Weekly
- [ ] Review performance metrics
- [ ] Check for updates
- [ ] Review user feedback
- [ ] Clean old logs

### ☐ Monthly
- [ ] Update dependencies
- [ ] Review security advisories
- [ ] Optimize database
- [ ] Review and update documentation

### ☐ Quarterly
- [ ] Performance audit
- [ ] Security audit
- [ ] Disaster recovery test
- [ ] Capacity planning review

## Sign-Off

### Deployment Team
- [ ] Developer sign-off: _________________ Date: _______
- [ ] DevOps sign-off: _________________ Date: _______
- [ ] QA sign-off: _________________ Date: _______
- [ ] Product sign-off: _________________ Date: _______

### Production Readiness
- [ ] All critical items completed
- [ ] All blockers resolved
- [ ] Rollback plan documented
- [ ] Team trained and ready
- [ ] Stakeholders informed

---

**Deployment Status**: ☐ Ready ☐ Not Ready

**Notes**:
_______________________________________________________
_______________________________________________________
_______________________________________________________

**Next Steps**:
_______________________________________________________
_______________________________________________________
_______________________________________________________
