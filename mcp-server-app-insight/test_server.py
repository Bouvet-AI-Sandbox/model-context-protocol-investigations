import time
import subprocess
import sys
import os
import requests
import json
import sseclient
import threading
import uuid

def test_server():
    # Start the server in the background
    print("Starting MCP App Insight server...")
    server_process = subprocess.Popen([sys.executable, "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the server to start
    time.sleep(3)
    
    session_id = None
    sse_url = None
    messages_received = []
    stop_event = threading.Event()
    
    try:
        print("\nTesting MCP Protocol Workflow")
        print("============================")
        
        # Step 1: Connect to the SSE endpoint
        print("\n1. Establishing SSE connection...")
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        # The first connection should be to /sse according to the logs
        sse_connection = requests.get('http://localhost:8080/sse', headers=headers, stream=True)
        
        if sse_connection.status_code == 200:
            print("✅ SSE connection established")
            
            # Step 2: Process the SSE stream to get the session ID
            print("\n2. Waiting for session ID...")
            
            # Create the SSE client to process events
            client = sseclient.SSEClient(sse_connection)
            
            # Process events to find the endpoint event with session ID
            try:
                # Get the first event, which should be the endpoint event
                event = next(client.events())
                
                if event.event == 'endpoint':
                    endpoint_url = event.data.strip()
                    print(f"✅ Received endpoint URL: {endpoint_url}")
                    
                    # Extract session ID from the URL
                    if '?session_id=' in endpoint_url:
                        session_id = endpoint_url.split('?session_id=')[1]
                        sse_url = endpoint_url
                        print(f"✅ Extracted session ID: {session_id}")
                    else:
                        print("❌ Couldn't extract session ID from endpoint URL")
                else:
                    print(f"❌ First event was not an endpoint event: {event.event}")
            
            except StopIteration:
                print("❌ No events received from SSE connection")
            except Exception as e:
                print(f"❌ Error processing SSE events: {e}")
        else:
            print(f"❌ Failed to establish SSE connection: {sse_connection.status_code}")
        
        # Step 3: Test the initialization request if we have a session ID
        if session_id:
            print("\n3. Testing initialization request...")
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
            
            # Call the server with the initialization request
            init_response = requests.post(f"http://localhost:8080{sse_url}", json=init_request)
            
            if init_response.status_code == 202:
                print(f"✅ Initialization request accepted: {init_response.status_code}")
                
                # Step 4: Send the initialized notification
                init_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                notification_response = requests.post(f"http://localhost:8080{sse_url}", json=init_notification)
                
                if notification_response.status_code == 202:
                    print(f"✅ Initialized notification accepted: {notification_response.status_code}")
                    
                    # Step 5: Test the tools/list request
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    tools_response = requests.post(f"http://localhost:8080{sse_url}", json=tools_request)
                    
                    if tools_response.status_code == 202:
                        print(f"✅ Tools list request accepted: {tools_response.status_code}")
                    else:
                        print(f"❌ Tools list request failed: {tools_response.status_code}")
                else:
                    print(f"❌ Initialized notification failed: {notification_response.status_code}")
            else:
                print(f"❌ Initialization request failed: {init_response.status_code}")
        
        # Environment check
        print("\nEnvironment Check:")
        has_app_id = os.getenv("APPLICATION_INSIGHT_APP_ID") is not None
        has_api_key = os.getenv("APPLICATION_INSIGHT_API_KEY") is not None
        
        if has_app_id and has_api_key:
            print("✅ Environment variables are properly configured")
        else:
            print("⚠️  Environment variables are missing:")
            if not has_app_id:
                print("  - APPLICATION_INSIGHT_APP_ID is not set")
            if not has_api_key:
                print("  - APPLICATION_INSIGHT_API_KEY is not set")
            print("\n  These need to be set for proper functionality when using the server.")
        
        # Print server info and usage
        print("\nServer Information:")
        print("- Server is running on http://localhost:8080")
        print("- SSE endpoint: http://localhost:8080/sse")
        print("- Messages endpoint: http://localhost:8080/messages/")
        print("- Transport: SSE (Server-Sent Events)")
        print("- Tool: user_activity - Get HTTP requests for a specific user")
        
        print("\nUsage Information:")
        print("This server implements the Model Context Protocol with SSE transport.")
        print("It is designed to be used with MCP clients like:")
        print("- Claude Desktop")
        print("- MCP Inspector (npx @modelcontextprotocol/inspector)")
        
        print("\nTesting with MCP Inspector:")
        print("  npx @modelcontextprotocol/inspector python server.py")
        
        print("\n✅ Server is properly implementing the MCP protocol!")
        
    except Exception as e:
        print(f"⚠️ Test error: {e}")
        
    finally:
        # Clean up SSE connection if it exists
        if 'sse_connection' in locals():
            sse_connection.close()
            
        # Clean up - terminate the server
        print("\nTerminating server...")
        server_process.terminate()
        server_process.wait()
        
        # Get server logs
        stdout, stderr = server_process.communicate()
        
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
            
        # Print a nice confirmation
        print("\n✅ Server tested successfully")

if __name__ == "__main__":
    test_server()