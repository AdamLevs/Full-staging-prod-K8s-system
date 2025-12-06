# Status Page Monitoring System

A robust, self-hosted full containerized status page monitoring system that tracks your services across multiple protocols and provides real-time health insights through an intuitive web interface.

## 🚀 Features

### Multi-Protocol Monitoring
- **HTTP/HTTPS** - Monitor web services and APIs with custom status code validation
- **ICMP Ping** - Network connectivity checks with latency tracking
- **TCP Port** - Socket-level service availability testing
- **DNS Resolution** - Domain name resolution monitoring

### Enterprise-Grade Architecture
- **FastAPI Backend** - High-performance Python API with automatic OpenAPI documentation
- **Celery Workers** - Distributed task processing for scalable monitoring
- **PostgreSQL Database** - Reliable data persistence with ACID compliance
- **Redis Queue** - Lightning-fast task queue and caching layer
- **React Frontend** - Modern, responsive dashboard built with Vite
- **Docker Deployment** - Containerized architecture for consistent environments

### Operational Excellence
- **Automated Health Checks** - Configurable intervals with Celery Beat scheduler
- **Real-time Dashboard** - Live status updates with historical tracking
- **Production Ready** - Full Docker Compose orchestration
- **Zero-Config Setup** - Automated environment generation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │ PostgreSQL DB   │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐
│  Celery Worker  │◄──►│  Redis Queue    │
│  (Background)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Quick Start

### Prerequisites

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **Make** utility

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AdamLevs/status-page.git
   cd status-page
   ```
   
 generate ssl environment variables
   ```bash
   make generate
   ```

2. **Launch the entire stack**
   ```bash
   make up
   ```

3. **Access your status page**
   - **Dashboard**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **API Endpoints**: http://localhost:8000/services

## 📋 Available Commands

The project includes a comprehensive Makefile for streamlined operations:

```bash
# generate environment variables
make generate

# run the application
make up

# shut down the application
make down

# make a full reset of the application
make reset

# MAKE A FULL RESET TO DOCKER VOLUMES! USE WITH CAUTION!
make destroy
```

## ⚙️ Configuration

### Environment Management

**⚠️ Important**: All environment variables are automatically generated via `backend/app/generate_env.py`.

To modify configuration:
1. Edit `backend/app/generate_env.py`
2. Run `make up` to regenerate `.env`

**Never manually edit the `.env` file** - it's regenerated on every deployment.

### Service Configuration

Add monitored services via the API or by modifying `initdb/init.sh`:

```json
{
  "name": "Google",
  "check_type": "Ping",
  "check_target": "8.8.8.8",
  "frequency": 0
}
```

### Supported Check Types

| Type   | Description           | Parameters                                     |
|--------|-----------------------|------------------------------------------------|
| `http` | HTTP/HTTPS requests   | `check_url`, `expected_status_code`, `timeout` |
| `ping` | ICMP ping tests       | `check_url` (hostname/IP), `timeout`           |
| `tcp`  | TCP port connectivity | `check_url` (host:port), `timeout`             |
| `dns`  | DNS resolution        | `check_url` (domain), `timeout`                |

### Database Initialization

Pre-populate services by editing `initdb/init.sh`:

```sql
INSERT INTO services (name, check_type, check_url, check_interval, expected_status_code) 
VALUES ('My Service', 'http', 'https://myservice.com', 60, 200);
```

## 🐳 Docker Services

| Service       | Port  | Description      |
|---------------|-------|------------------|
| Frontend      | 3000  | React dashboard  |
| Backend       | 8000  | FastAPI server   |
| PostgreSQL    | 55432 | Database         |
| Redis         | 6379  | Task queue       |
| Celery Worker | -     | Background tasks |
| Celery Beat   | -     | Task scheduler   |

## 📊 Monitoring & Observability

- **Health Checks**: Automated service monitoring every 60 seconds
- **Historical Data**: Complete audit trail of all checks
- **Real-time Updates**: WebSocket-based live dashboard
- **API Metrics**: Built-in FastAPI metrics and documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built by [@AdamLevs](https://github.com/AdamLevs) (2025)**
