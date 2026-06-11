# SPARQL CLI Dispatcher

A production-grade Command-Line Interface (CLI) tool designed to map natural language intents into executable SPARQL queries. The system dispatches these queries to a local Apache Jena Fuseki triple store container holding semantic publication records.

## Project Architecture

- **Backend:** Apache Jena Fuseki deployed inside a Docker container.
- **Data Layer:** `data/publications.ttl` containing 1,265 Semantic Web triples.
- **CLI Dispatcher:** Python script (`query.py`) leveraging `argparse`, `requests` with dynamic content negotiation, and type-hinted object-oriented patterns.
- **Testing:** Unit test suite using `pytest` and `unittest.mock` for isolated verification.
- **Setup Automation:** `setup.sh` for one-step environment initialization.

## Prerequisites

Make sure you have:

- Docker and Docker Compose
- Python 3.12+
- Bash shell

## Setup & Installation

### Recommended: Automated Setup

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This script:

- creates the Python virtual environment
- installs the required dependencies
- starts the Fuseki Docker container
- loads `data/publications.ttl` into Fuseki

### Manual Setup

If you prefer to run the steps yourself:

1. Start the Fuseki server:

```bash
docker compose up -d
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Load the dataset:

```bash
curl -X POST   -H "Content-Type: text/turtle"   -T data/publications.ttl   "http://admin:admin@localhost:3030/publications/data?default"
```

Expected response:

```json
{
  "count": 1265,
  "tripleCount": 1265,
  "quadCount": 0
}
```

## CLI Usage Guide

Run natural language intents directly from the terminal. The CLI automatically selects the correct SPARQL query type and handles content negotiation.

### Intent 1: List Authors at NeurIPS (SELECT)

Retrieves a distinct, alphabetically sorted list of authors published at NeurIPS.

```bash
python query.py "list authors at NeurIPS"
```

### Intent 2: Papers Per Topic (SELECT + GROUP BY)

Counts papers grouped by topic and sorts results in descending order.

```bash
python query.py "papers per topic"
```

### Intent 3: Top 5 Cited Papers (SELECT + ORDER + LIMIT)

Returns the five most cited research papers.

```bash
python query.py "top 5 cited"
```

### Intent 4: Check 2024 Publications (ASK)

Checks whether any publication exists from 2024.

```bash
python query.py "is there any paper from 2024"
```

Expected output:

```text
Result: YES (True)
```

### Intent 5: Extract 2024 Sub-Graph (CONSTRUCT)

Builds and exports a Turtle RDF subgraph containing 2024 publication data.

```bash
python query.py "construct 2024 papers sub-graph"
```

## Error Handling

For invalid or unsupported intents:

```bash
python query.py "hello world"
```

The CLI exits with status code `1` and displays the supported commands.

## Automated Testing Suite

The project includes isolated tests using `pytest`, `unittest.mock`, and network request mocking. Tests run without requiring a live Fuseki server.

Run:

```bash
pytest -v
```

Expected output:

```text
5 passed in 0.09s
```

## Project Tree

```text
SPARQL-CLI-DISPATCHER
├── data
│   └── publications.ttl
├── tests
│   └── test_dispatcher.py
├── .gitignore
├── conftest.py
├── docker-compose.yml
├── query.py
├── README.md
├── requirements.txt
└── setup.sh
```
