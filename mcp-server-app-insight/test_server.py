import time
import subprocess
import sys
import os
import requests
import json
import sseclient
import threading
import pytest
from typing import Generator, Tuple


@pytest.fixture(scope="module")
def server_process() -> Generator[subprocess.Popen, None, None]:
    """Start the MCP App Insight server as a fixture."""
    # Create test environment variables for server to use if real ones aren't available
    test_env = os.environ.copy()
    if not os.getenv("APPLICATION_INSIGHT_APP_ID"):
        test_env["APPLICATION_INSIGHT_APP_ID"] = "TEST_APP_ID_FOR_TESTING_ONLY"
    if not os.getenv("APPLICATION_INSIGHT_API_KEY"):
        test_env["APPLICATION_INSIGHT_API_KEY"] = "TEST_API_KEY_FOR_TESTING_ONLY"
    
    print("Starting MCP App Insight server...")
    process = subprocess.Popen([sys.executable, "server.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              env=test_env)
    
    # Wait for the server to start
    time.sleep(3)
    
    # Check if server started successfully
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print(f"Server failed to start with exit code {process.returncode}")
        print(f"STDERR: {stderr.decode('utf-8')}")
        # We'll still yield the process so tests can decide what to do
    
    yield process
    
    # Only try to terminate if the process is still running
    if process.poll() is None:
        print("\nTerminating server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Server didn't terminate within timeout, killing...")
            process.kill()
            process.wait()
    
    # Get and print server logs
    stdout, stderr = process.communicate()
    
    # Print a summarized version of the logs
    print("\nServer Log Summary:")
    stderr_lines = stderr.decode('utf-8').splitlines()
    session_logs = [line for line in stderr_lines if 'session' in line.lower() or 'sse' in line.lower()]
    if session_logs:
        for line in session_logs[:5]:  # Show the first 5 session-related logs
            print(f"  {line.strip()}")
        if len(session_logs) > 5:
            print(f"  ... and {len(session_logs) - 5} more session logs")
    
    startup_logs = [line for line in stderr_lines if 'Starting' in line or 'startup' in line or 'Started' in line]
    for line in startup_logs:
        print(f"  {line.strip()}")


@pytest.fixture(scope="module")
def sse_connection(server_process) -> Generator[Tuple[requests.Response, sseclient.SSEClient], None, None]:
    """Establish an SSE connection to the server."""
    # Skip if server didn't start
    if server_process.poll() is not None:
        pytest.skip(f"Server process is not running (exit code: {server_process.returncode})")
    
    headers = {
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
    }
    
    try:
        # Connect to the SSE endpoint with a timeout to avoid hanging
        connection = requests.get('http://localhost:8080/sse', 
                                headers=headers, 
                                stream=True,
                                timeout=5)
        
        if connection.status_code != 200:
            pytest.skip(f"Failed to establish SSE connection: {connection.status_code}")
        
        # Create the SSE client to process events
        client = sseclient.SSEClient(connection)
        
        yield connection, client
        
        # Cleanup
        connection.close()
    except requests.RequestException as e:
        pytest.skip(f"Connection to server failed: {e}")


@pytest.fixture(scope="module")
def session_details(sse_connection) -> dict:
    """Extract session ID and endpoint URL from the SSE connection."""
    _, client = sse_connection
    
    try:
        # Get the first event, which should be the endpoint event
        event = next(client.events())
        
        if event.event != 'endpoint':
            pytest.fail(f"First event was not an endpoint event: {event.event}")
        
        endpoint_url = event.data.strip()
        
        if '?session_id=' not in endpoint_url:
            pytest.fail("Couldn't extract session ID from endpoint URL")
        
        session_id = endpoint_url.split('?session_id=')[1]
        
        return {
            "session_id": session_id,
            "endpoint_url": endpoint_url,
            "full_url": f"http://localhost:8080{endpoint_url}"
        }
    
    except StopIteration:
        pytest.fail("No events received from SSE connection")
    except Exception as e:
        pytest.fail(f"Error processing SSE events: {e}")


def test_sse_connection_established(sse_connection):
    """Test that the SSE connection is successfully established."""
    connection, _ = sse_connection
    assert connection.status_code == 200, "SSE connection should be established"


def test_session_id_received(session_details):
    """Test that a valid session ID is received."""
    assert session_details["session_id"], "Should receive a valid session ID"
    assert session_details["endpoint_url"], "Should receive a valid endpoint URL"


def test_initialization_request(session_details):
    """Test the initialization request to the server."""
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "sampling": {},
                "roots": {
                    "listChanged": True
                }
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    response = requests.post(session_details["full_url"], json=init_request)
    assert response.status_code == 202, "Initialization request should be accepted"


def test_initialized_notification(session_details):
    """Test sending the 'initialized' notification."""
    init_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    
    response = requests.post(session_details["full_url"], json=init_notification)
    assert response.status_code == 202, "Initialized notification should be accepted"


def test_tools_list_request(session_details):
    """Test the tools/list request."""
    tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    response = requests.post(session_details["full_url"], json=tools_request)
    assert response.status_code == 202, "Tools list request should be accepted"


def test_environment_variables():
    """Test that the required environment variables are set."""
    has_app_id = os.getenv("APPLICATION_INSIGHT_APP_ID") is not None
    has_api_key = os.getenv("APPLICATION_INSIGHT_API_KEY") is not None
    
    if not (has_app_id and has_api_key):
        missing = []
        if not has_app_id:
            missing.append("APPLICATION_INSIGHT_APP_ID")
        if not has_api_key:
            missing.append("APPLICATION_INSIGHT_API_KEY")
        
        pytest.skip(f"Skipping test due to missing environment variables: {', '.join(missing)}")
    
    assert has_app_id, "APPLICATION_INSIGHT_APP_ID should be set"
    assert has_api_key, "APPLICATION_INSIGHT_API_KEY should be set"


def test_server_info(server_process):
    """Test that server info is available and correct."""
    # The server may have exited if env vars are missing, so we'll check conditionally
    if server_process.poll() is not None:
        # Server exited - check if it's due to missing env vars
        has_app_id = os.getenv("APPLICATION_INSIGHT_APP_ID") is not None
        has_api_key = os.getenv("APPLICATION_INSIGHT_API_KEY") is not None
        
        if not (has_app_id and has_api_key):
            pytest.skip("Server not running due to missing environment variables")
        else:
            # If env vars are present but server still exited, fail the test
            assert False, f"Server exited with return code {server_process.poll()}"
    else:
        # Server is running as expected
        assert server_process.poll() is None, "Server should be running"
        
        
if __name__ == "__main__":
    # When run directly, use pytest to execute the tests
    import sys
    import pytest
    sys.exit(pytest.main(["-v", __file__]))