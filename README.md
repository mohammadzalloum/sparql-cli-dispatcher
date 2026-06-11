# SPARQL CLI Dispatcher

A production-grade Command-Line Interface (CLI) tool designed to map natural language intents into executable SPARQL queries. The system dispatches these queries to a local Apache Jena Fuseki triple store container holding semantic publication records.

## Project Architecture

- **Backend:** Apache Jena Fuseki deployed inside a Docker container.
- **Data Layer:** `publications.ttl` containing 1,265 Semantic Web Triples.
- **CLI Dispatcher:** Python script (`query.py`) leveraging `argparse`, `requests` with dynamic content negotiation, and type-hinted Object-Oriented patterns.
- **Testing:** Comprehensive unit test suite using `pytest` along with `unittest.mock` for fully isolated verification.

---

## Prerequisites

Ensure you have the following installed on your machine:
- **Docker & Docker Compose**
- **Python 3.12+**
- A virtual environment tool (e.g., `venv`)

---

## Setup & Installation

### 1. Start the Fuseki Server
Launch the pre-configured Apache Jena Fuseki database container in detached mode:
```bash
docker compose up -d
```

### 2. Ingest Dataset (Triples)
Upload the semantic publications graph data (`data/publications.ttl`) into the Fuseki default dataset using `curl`:
```bash
curl -X POST \
  -H "Content-Type: text/turtle" \
  -T data/publications.ttl \
  "http://admin:admin@localhost:3030/publications/data?default"
```
*Expected response upon success:*
```json
{ 
  "count" : 1265 ,
  "tripleCount" : 1265 ,
  "quadCount" : 0
}
```

### 3. Initialize Python Environment
Set up your virtual environment and install the required dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## CLI Usage Guide

Execute natural language intents directly from your terminal. The tool automatically negotiates content types (JSON/Turtle) based on the target SPARQL query pattern.

### Intent 1: List Authors at NeurIPS (SELECT)
Retrieves a distinct, alphabetically sorted list of authors published at NeurIPS.
```bash
python query.py "list authors at NeurIPS"
```

### Intent 2: Papers Per Topic (SELECT with Group By)
Counts and aggregates the total number of papers assigned to each topic, ordered descendingly.
```bash
python query.py "papers per topic"
```

### Intent 3: Top 5 Cited Papers (SELECT with Order & Limit)
Returns the top 5 most cited research papers along with their specific citation counts.
```bash
python query.py "top 5 cited"
```

### Intent 4: Check 2024 Publications (ASK)
Returns a direct Boolean check verifying whether any paper was published in the year 2024.
```bash
python query.py "is there any paper from 2024"
```
*Expected Output:* `Result: YES (True)`

### Intent 5: Extract 2024 Sub-Graph (CONSTRUCT)
Constructs and exports a dedicated Turtle RDF sub-graph isolating 2024 publication headers.
```bash
python query.py "construct 2024 papers sub-graph"
```

### Error Handling & Capabilities Help
If an invalid or empty intent is provided, the CLI exits with non-zero status code `1` and prints all supported options:
```bash
python query.py "hello world"
```

---

## Automated Testing Suite

The project includes an isolated testing suite utilizing `conftest.py` anchoring and network mocking to execute unit tests without depending on a live server.

To run the automated tests in verbose mode, execute:
```bash
pytest -v
```
*Expected Output:* `5 passed in 0.09s`