# Stabilizer Tableau Clifford Sim

> **Domain:** Quantum Computing / Stabilizer Circuit Simulation
> **Reference:** Aaronson-Gottesman Clifford Algorithm

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Stabilizer Tableau Clifford Sim is a Python implementation of the Aaronson-Gottesman stabilizer tableau algorithm for fast simulation of Clifford circuits. It provides:

- **Stabilizer Tableau Engine**: Binary symplectic representation for efficient Clifford gate simulation
- **Multi-Agent Coordination**: Distributed worker architecture for parallel circuit evaluation
- **HMAC-SHA256 Audit Trail**: Cryptographically signed, tamper-evident logging for all operations
- **PHI Outbound Guard**: Regex-based detection and blocking of sensitive identifiers in outputs
- **FastAPI REST API**: OpenAPI-compatible endpoints for remote circuit evaluation
- **CLI Interface**: Command-line tools for batch processing and interactive simulation

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Stabilizer State Generator**: Custom stabilizer group generation with configurable thresholds
- **Optimized Tableau Simulator**: Bitwise symplectic representation for >10x speedup over naive implementations
- **Frontier Domain Engine**: Primary/secondary parameter evaluation with boundary detection
- **Multi-Agent Workers**: Specialized sub-agents for QC, safety, and protocol conformance
- **Active Learning Engine**: Bayesian calibration of worker reliability weights
- **Prometheus Metrics**: Operational telemetry export for monitoring

---

## 💻 CLI Quickstart & Usage

### 1. Interactive Audit Mode
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. System Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier
- `--target`: Target entity or cryptographic key identifier
- `--primary`: Primary measurement value (float)
- `--secondary`: Secondary metric value (float)
- `--critical`: Flag for emergency escalation (boolean)
- `--status`: Status descriptor (NOMINAL, DISCORDANT, ANOMALY, etc.)

---

## 🛡️ Security & Architecture

* **Zero-PHI Outbound Interceptor:** Regex-based inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with integrity verification.
* **Secure Key Management:** Audit signing key sourced from `AUDIT_SECRET_KEY` environment variable or auto-generated via `secrets.token_hex`.
* **FastAPI REST API:** OpenAPI 3.1 compatible endpoints with Pydantic validation.
* **Prometheus Telemetry:** Operational metrics exposed at `/metrics`.

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t stabilizer-tableau-clifford-sim .
docker run -p 8000:8000 stabilizer-tableau-clifford-sim
```

---

## 📁 Project Structure

```
stabilizer-tableau-clifford-sim/
├── agents/                      # Multi-agent coordination layer
│   ├── __init__.py
│   ├── api.py                   # FastAPI REST endpoints
│   ├── base.py                  # Security, PHI guard, audit trail
│   ├── learning.py              # Bayesian calibration engine
│   ├── llm_factory.py           # LLM provider abstraction
│   ├── metrics.py               # Prometheus metrics collector
│   ├── models.py                # Pydantic data models
│   ├── streamer.py              # WebSocket telemetry broadcaster
│   ├── supervisor.py            # Master orchestrator
│   └── workers.py               # Specialized evaluation workers
├── stabilizer_tableau/          # Core stabilizer tableau engine
│   ├── __init__.py
│   ├── agents.py                # Sub-agent implementations
│   ├── cli.py                   # CLI for stabilizer tableau
│   ├── engine.py                # Frontier domain engine
│   ├── models.py                # Data models
│   └── server.py                # FastAPI server factory
├── tests/                       # Pytest test suite
│   ├── test_enrichment.py
│   ├── test_stabilizer_tableau.py
│   └── test_stabilizer_tableau_clifford_sim.py
├── web/                         # Operations console (HTML/JS)
│   └── index.html
├── cli.py                       # Main CLI entry point
├── simulator.py                 # High-throughput simulation
├── enrichment.py                # Feature enrichment engines
├── pyproject.toml               # Project configuration
├── Dockerfile                   # Container build
├── docker-compose.yml           # Multi-service orchestration
├── sample.csv                   # Sample batch input
├── sample_payload.json          # Sample API payload
└── benchmark_dataset.json       # Golden benchmark test cases
```

---

## 🔧 Configuration

| Environment Variable | Description | Default |
|:---------------------|:------------|:--------|
| `AUDIT_SECRET_KEY` | HMAC signing key for audit trail | Auto-generated (random) |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
