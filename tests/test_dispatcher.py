import pytest
import sys
import requests
from unittest.mock import patch, MagicMock
from query import SPARQL_MAPPING, main, SparqlDispatcher

def test_sparql_mapping_structure():
    """Verify that all required intents exist and contain valid SPARQL syntax structure."""
    expected_intents = [
        "list authors at NeurIPS",
        "papers per topic",
        "top 5 cited",
        "is there any paper from 2024",
        "construct 2024 papers sub-graph"
    ]
    for intent in expected_intents:
        assert intent in SPARQL_MAPPING
        query = SPARQL_MAPPING[intent]
        assert "PREFIX" in query
        
        # Cross-validate query types against expectations
        if "sub-graph" in intent:
            assert "CONSTRUCT" in query.upper()
        elif "is there" in intent:
            assert "ASK" in query.upper()
        else:
            assert "SELECT" in query.upper()

@patch('sys.argv', ['query.py', 'unsupported intent'])
def test_unknown_intent_exits_nonzero():
    """Verify that an invalid CLI intent triggers an error and exits with code 1."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1

@patch('requests.Session.post')
def test_content_negotiation_for_select_queries(mock_post):
    """Verify SELECT queries correctly request and parse application/sparql-results+json."""
    # Setup mock response for a SELECT query
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"head": {"vars": ["p"]}, "results": {"bindings": []}}
    mock_post.return_value = mock_response

    dispatcher = SparqlDispatcher("http://fake-endpoint")
    result = dispatcher.execute(SPARQL_MAPPING["top 5 cited"])

    # Validate that JSON headers were sent and JSON payload was parsed
    assert isinstance(result, dict)
    mock_post.assert_called_once()
    headers_sent = mock_post.call_args[1]['headers']
    assert headers_sent['Accept'] == 'application/sparql-results+json'

@patch('requests.Session.post')
def test_content_negotiation_for_construct_queries(mock_post):
    """Verify CONSTRUCT queries correctly request and return text/turtle format."""
    # Setup mock response for a CONSTRUCT query
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "@prefix : <http://example.org/> . :paper01 :year 2024 ."
    mock_post.return_value = mock_response

    dispatcher = SparqlDispatcher("http://fake-endpoint")
    result = dispatcher.execute(SPARQL_MAPPING["construct 2024 papers sub-graph"])

    # Validate that Turtle headers were sent and text payload was returned
    assert isinstance(result, str)
    mock_post.assert_called_once()
    headers_sent = mock_post.call_args[1]['headers']
    assert headers_sent['Accept'] == 'text/turtle'

@patch('requests.Session.post')
def test_dispatcher_error_resilience(mock_post):
    """Verify dispatcher gracefully handles connection errors and returns None."""
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

    dispatcher = SparqlDispatcher("http://fake-endpoint")
    result = dispatcher.execute(SPARQL_MAPPING["top 5 cited"])

    assert result is None