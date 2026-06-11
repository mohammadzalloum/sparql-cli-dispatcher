import argparse
import sys
import os
import requests
from typing import Optional, Union, Dict, Any

# Read endpoint from environment variables or use the local default
FUSEKI_URL = os.getenv("FUSEKI_URL", "http://localhost:3030/publications/query")

# Fixed-vocabulary mapping of natural language intents to SPARQL queries
SPARQL_MAPPING = {
    "list authors at NeurIPS": """
        PREFIX : <http://aispire.example.org/publications/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?authorLabel WHERE {
            ?paper a :Paper ;
                   :publishedIn :NeurIPS ;
                   :authoredBy ?author .
            ?author rdfs:label ?authorLabel .
        } ORDER BY ?authorLabel
    """,
    "papers per topic": """
        PREFIX : <http://aispire.example.org/publications/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?topicLabel (COUNT(?paper) AS ?count) WHERE {
            ?paper a :Paper ;
                   :topic ?topic .
            ?topic rdfs:label ?topicLabel .
        } GROUP BY ?topicLabel ORDER BY DESC(?count)
    """,
    "top 5 cited": """
        PREFIX : <http://aispire.example.org/publications/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?paperLabel ?citations WHERE {
            ?paper a :Paper ;
                   rdfs:label ?paperLabel ;
                   :citationCount ?citations .
        } ORDER BY DESC(?citations) LIMIT 5
    """,
    "is there any paper from 2024": """
        PREFIX : <http://aispire.example.org/publications/>
        ASK {
            ?paper a :Paper ;
                   :year 2024 .
        }
    """,
    "construct 2024 papers sub-graph": """
        PREFIX : <http://aispire.example.org/publications/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        CONSTRUCT {
            ?paper rdfs:label ?label ;
                   :year ?year .
        } WHERE {
            ?paper a :Paper ;
                   rdfs:label ?label ;
                   :year ?year .
            FILTER(?year = 2024)
        } LIMIT 10
    """
}

class SparqlDispatcher:
    """A professional CLI dispatcher for executing NLP intents as SPARQL queries."""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.session = requests.Session()  # Using Session for better connection pooling and performance

    def execute(self, query: str) -> Optional[Union[Dict[str, Any], str]]:
        """Executes the SPARQL query and handles content negotiation."""
        is_construct = "CONSTRUCT" in query.upper()
        headers = {'Accept': 'text/turtle' if is_construct else 'application/sparql-results+json'}
        
        try:
            response = self.session.post(self.endpoint, data={'query': query}, headers=headers, timeout=10)
            response.raise_for_status()  # Throws an exception for non-200 responses
            return response.text if is_construct else response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Fuseki Endpoint: {e}", file=sys.stderr)
            return None

    def display_results(self, data: Union[Dict[str, Any], str, None]) -> None:
        """Parses and formats the output cleanly based on the query type."""
        if data is None:
            return

        # 1. Output for CONSTRUCT queries (String/Turtle)
        if isinstance(data, str):
            print("\n--- Constructed Sub-Graph (Turtle) ---")
            print(data.strip())
            return

        # 2. Output for ASK queries (Boolean)
        if "boolean" in data:
            result_str = "YES (True)" if data["boolean"] else "NO (False)"
            print(f"\nResult: {result_str}")
            return

        # 3. Output for SELECT queries (Tabular format)
        if "results" in data and "bindings" in data["results"]:
            bindings = data["results"]["bindings"]
            if not bindings:
                print("\nNo results found.")
                return
                
            variables = data["head"]["vars"]
            
            # Print tabular header row
            print("\n" + " | ".join(f"{var.upper(): <25}" for var in variables))
            print("-" * (28 * len(variables)))
            
            # Print tabular data rows
            for row in bindings:
                clean_row = []
                for var in variables:
                    val = row.get(var, {}).get("value", "")
                    # Extract the local name if the value is a full URI path
                    clean_row.append(val.split('/')[-1])
                    
                print(" | ".join(f"{str(val): <25}" for val in clean_row))
            print("-" * (28 * len(variables)))

def main():
    parser = argparse.ArgumentParser(description="Advanced SPARQL CLI Dispatcher", add_help=False)
    parser.add_argument("intent", nargs="?", type=str)
    args = parser.parse_args()
    
    # Input validation
    if not args.intent or args.intent not in SPARQL_MAPPING:
        print("Error: Unknown or missing intent.\n", file=sys.stderr)
        print("Supported intents are:", file=sys.stderr)
        for supported_intent in SPARQL_MAPPING.keys():
            print(f"  - \"{supported_intent}\"", file=sys.stderr)
        sys.exit(1)

    # Core execution flow
    dispatcher = SparqlDispatcher(FUSEKI_URL)
    sparql_query = SPARQL_MAPPING[args.intent]
    
    raw_results = dispatcher.execute(sparql_query)
    dispatcher.display_results(raw_results)

if __name__ == "__main__":
    main()