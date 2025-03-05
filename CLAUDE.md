# CLAUDE.md - Build, Test, and Style Guide

## Commands
- **Python Apps**: `pip install -r requirements.txt` for install, `python main.py` to run
- **App Insights Server**: `pytest` or `python test_server.py` for testing
- **TypeScript App**: `npm run build` to compile, `npm start` to run
- **MCP Client**: `goose session` to run client

## Style Guidelines
- **Python**:
  - Imports order: stdlib, third-party, local (alphabetically within groups)
  - Type hints with `typing` module (Dict, Any, Optional, Tuple)
  - Exception handling: specific exceptions, contextual logging
  - Pytest for testing with fixtures and clear test function naming

- **TypeScript**:
  - ES modules syntax with named imports
  - Strong typing with interfaces
  - Private methods with `private` keyword
  - Error objects with code enumeration

## Patterns
- Validate environment variables with proper error messages
- JSON-RPC and SSE for MCP communication
- Structured error handling with contextual logging
- Pydantic for data validation
- Fixtures for resource setup/teardown in tests