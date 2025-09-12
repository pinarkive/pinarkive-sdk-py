# Pinarkive Python SDK

Python client for the Pinarkive API v2.3.1. Easy IPFS file management with directory DAG uploads, file renaming, and enhanced API key management. Includes type hints for better IDE support and Pythonic usage patterns.

## Installation

```bash
pip install pinarkive-sdk-py
```

## Quick Start

```python
from pinarkive_client import PinarkiveClient

# Initialize with API key
client = PinarkiveClient(api_key="your-api-key-here")

# Upload a file
result = client.upload_file("document.pdf")
print(f"File uploaded: {result.json()['cid']}")

# Generate API key
token = client.generate_token("my-app", {
    "expires_in_days": 30
})
print(f"New API key: {token.json()['token']}")
```

## Authentication

The SDK supports two authentication methods:

### API Key Authentication (Recommended)
```python
client = PinarkiveClient(api_key="your-api-key-here")
```
**Note:** The SDK automatically sends the API key using the `Authorization: Bearer` header format, not `X-API-Key`.

### JWT Token Authentication
```python
client = PinarkiveClient(token="your-jwt-token-here")
```

## Basic Usage

### File Upload
```python
# Upload single file
result = client.upload_file("document.pdf")
response_data = result.json()
print(f"CID: {response_data['cid']}")
print(f"Status: {response_data['status']}")
```

### Directory Upload
```python
# Upload directory from local path
result = client.upload_directory("/path/to/directory")
print(f"Directory CID: {result.json()['cid']}")
```

### List Uploads
```python
# List all uploaded files with pagination
result = client.list_uploads(page=1, limit=20)
response_data = result.json()
print(f"Uploads: {response_data['uploads']}")
print(f"Total: {response_data['pagination']['total']}")
```

## Advanced Features

### Directory DAG Upload
Upload entire directory structures as DAG (Directed Acyclic Graph):

```python
# Create project structure
project_files = {
    "src/index.py": "print('Hello World')",
    "src/utils.py": "def utils(): pass",
    "requirements.txt": "requests>=2.31.0",
    "README.md": "# My Project\n\nThis is my project."
}

# Upload as DAG
result = client.upload_directory_dag(project_files, dir_name="my-project")
response_data = result.json()
print(f"DAG CID: {response_data['dagCid']}")
print(f"Files: {response_data['files']}")
```

### Directory Cluster Upload
```python
# Upload using cluster-based approach
files = [
    {"path": "file1.txt", "content": "Content 1"},
    {"path": "file2.txt", "content": "Content 2"}
]

result = client.upload_directory_cluster(files)
print(f"Cluster CID: {result.json()['cid']}")
```

### Upload File to Existing Directory
```python
# Add file to existing directory
result = client.upload_file_to_directory("new-file.txt", "existing-directory-path")
print(f"File added to directory: {result.json()['cid']}")
```

### File Renaming
```python
# Rename an uploaded file
result = client.rename_file("upload-id-here", "new-file-name.pdf")
print(f"File renamed: {result.json()['updated']}")
```

### File Removal
```python
# Remove a file from storage
result = client.remove_file("QmYourCIDHere")
print(f"File removed: {result.json()['success']}")
```

### Pinning Operations

#### Basic CID Pinning
```python
# Pin with filename
result = client.pin_cid("QmYourCIDHere", "my-file.pdf")
print(f"CID pinned: {result.json()['pinned']}")

# Pin without filename (backend will use default)
result2 = client.pin_cid("QmYourCIDHere")
print(f"CID pinned: {result2.json()['pinned']}")
```

#### Pin with Custom Name
```python
result = client.pin_cid_with_name("QmYourCIDHere", "my-important-file")
print(f"CID pinned with name: {result.json()['pinned']}")
```

### API Key Management

#### Generate API Key
```python
# Basic token generation
token = client.generate_token("my-app")

# Advanced token with options
token = client.generate_token("my-app", {
    "expires_in_days": 30,
    "ip_allowlist": ["192.168.1.1", "10.0.0.1"],
    "permissions": ["upload", "pin"]
})
print(f"New API key: {token.json()['token']}")
```

#### List API Keys
```python
tokens = client.list_tokens()
print(f"API Keys: {tokens.json()['tokens']}")
```

#### Revoke API Key
```python
result = client.revoke_token("my-app")
print(f"Token revoked: {result.json()['revoked']}")
```

## Type Hints Support

The SDK includes comprehensive type hints for better IDE support:

```python
from typing import Dict, Any, Optional
from pinarkive_client import PinarkiveClient

# Type hints provide better autocomplete and error checking
client = PinarkiveClient(api_key="your-key")

# IDE will show parameter types and return types
def upload_project_files(files: Dict[str, str]) -> Any:
    return client.upload_directory_dag(files, dir_name="project")

# Type hints for options
token_options: Dict[str, Any] = {
    "expires_in_days": 30,
    "ip_allowlist": ["192.168.1.1"]
}
token = client.generate_token("my-app", token_options)
```

## Error Handling

```python
import requests

try:
    result = client.upload_file("document.pdf")
    print("Success:", result.json())
except requests.exceptions.RequestException as e:
    if hasattr(e, 'response') and e.response is not None:
        print(f"API Error: {e.response.status_code}")
        print(f"Response: {e.response.json()}")
    else:
        print(f"Network Error: {e}")
```

## Integration Examples

### Django Integration
```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pinarkive_client import PinarkiveClient
import json

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        client = PinarkiveClient(api_key=settings.PINARKIVE_API_KEY)
        
        uploaded_file = request.FILES['file']
        # Save temporarily
        with open(f'/tmp/{uploaded_file.name}', 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        try:
            result = client.upload_file(f'/tmp/{uploaded_file.name}')
            return JsonResponse(result.json())
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

### Flask Integration
```python
from flask import Flask, request, jsonify
from pinarkive_client import PinarkiveClient
import os

app = Flask(__name__)
client = PinarkiveClient(api_key=os.environ.get('PINARKIVE_API_KEY'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save temporarily
    temp_path = f'/tmp/{file.filename}'
    file.save(temp_path)
    
    try:
        result = client.upload_file(temp_path)
        os.remove(temp_path)  # Clean up
        return jsonify(result.json())
    except Exception as e:
        os.remove(temp_path)  # Clean up on error
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    try:
        result = client.list_uploads()
        return jsonify(result.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### FastAPI Integration
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from pinarkive_client import PinarkiveClient
import tempfile
import os

app = FastAPI()
client = PinarkiveClient(api_key=os.environ.get('PINARKIVE_API_KEY'))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        
        try:
            result = client.upload_file(temp_file.name)
            os.unlink(temp_file.name)  # Clean up
            return result.json()
        except Exception as e:
            os.unlink(temp_file.name)  # Clean up on error
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files(page: int = 1, limit: int = 10):
    try:
        result = client.list_uploads(page=page, limit=limit)
        return result.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## API Reference

### Constructor
```python
PinarkiveClient(token: Optional[str] = None, api_key: Optional[str] = None, base_url: str = 'https://api.pinarkive.com/api/v2')
```
- `token`: Optional JWT token for authentication
- `api_key`: Optional API key for authentication
- `base_url`: Base URL for the API (defaults to production)

### File Operations
- `uploadFile(file_path: str)` - Upload single file
- `uploadDirectory(dir_path: str)` - Upload directory recursively (calls uploadFile for each file)
- `uploadDirectoryDAG(files_dict: Dict[str, Any], dir_name: Optional[str] = None)` - Upload directory as DAG structure
- `renameFile(upload_id: str, new_name: str)` - Rename uploaded file
- `removeFile(cid: str)` - Remove file from storage

### Pinning Operations
- `pinCid(cid: str, filename: Optional[str] = None)` - Pin CID to account with optional filename

### User Operations
- `listUploads(page: int = 1, limit: int = 10)` - List uploaded files

### Token Management
- `generateToken(name: str, options: Optional[Dict[str, Any]] = None)` - Generate API key
- `listTokens()` - List all API keys
- `revokeToken(name: str)` - Revoke API key


### Status & Monitoring
- `getStatus(cid: str)` - Get file status
- `getAllocations(cid: str)` - Get storage allocations

## Examples

### Complete File Management Workflow
```python
from pinarkive_client import PinarkiveClient

def manage_files():
    client = PinarkiveClient(api_key="your-api-key")
    
    try:
        # 1. Upload a file
        result = client.upload_file("document.pdf")
        upload_data = result.json()
        print(f"Uploaded: {upload_data['cid']}")
        
        # 2. Pin the CID with a custom name
        pin_result = client.pin_cid_with_name(upload_data['cid'], "important-document")
        print(f"Pinned: {pin_result.json()['pinned']}")
        
        # 3. Rename the file
        if 'uploadId' in upload_data:
            rename_result = client.rename_file(upload_data['uploadId'], "my-document.pdf")
            print(f"Renamed: {rename_result.json()['updated']}")
        
        # 4. List all uploads
        uploads = client.list_uploads()
        print(f"All uploads: {uploads.json()['uploads']}")
        
    except Exception as e:
        print(f"Error: {e}")

manage_files()
```

### Directory Upload Workflow
```python
def upload_project():
    client = PinarkiveClient(api_key="your-api-key")
    
    # Create project structure
    project_files = {
        "src/main.py": "print('Hello World')",
        "src/utils.py": "def helper(): pass",
        "requirements.txt": "requests>=2.31.0",
        "README.md": "# My Project\n\nThis is my project."
    }
    
    try:
        result = client.upload_directory_dag(project_files, dir_name="my-project")
        response_data = result.json()
        print(f"Project uploaded: {response_data['dagCid']}")
        print(f"Files: {response_data['files']}")
    except Exception as e:
        print(f"Upload failed: {e}")

upload_project()
```

### Batch File Processing
```python
import os
from pathlib import Path

def upload_directory_contents(directory_path: str):
    client = PinarkiveClient(api_key="your-api-key")
    
    files_dict = {}
    directory = Path(directory_path)
    
    # Recursively collect all files
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            # Get relative path from directory
            relative_path = str(file_path.relative_to(directory))
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            files_dict[relative_path] = content
    
    try:
        result = client.upload_directory_dag(files_dict, dir_name=directory.name)
        print(f"Directory uploaded: {result.json()['dagCid']}")
    except Exception as e:
        print(f"Upload failed: {e}")

# Usage
upload_directory_contents("./my-project")
```

## Publishing Instructions

### Publishing to PyPI

This package is published to PyPI using the following process:

```bash
# Update version in pyproject.toml
python -m build
twine upload dist/*
```

### Development Build

For testing before publishing:

```bash
# Build the package
python -m build

# Upload to TestPyPI for testing
twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ pinarkive-sdk-py
```

### Version Management

- Update version in `pyproject.toml`
- Build the package with `python -m build`
- Upload to PyPI with `twine upload dist/*`
- Tag the release in git: `git tag v2.3.1 && git push origin v2.3.1`

### PyPI Best Practices

- Use semantic versioning (2.3.1, 2.4.0, etc.)
- Test on TestPyPI before publishing to production
- Include comprehensive README and documentation
- Use proper classifiers in pyproject.toml

## Support

For issues or questions:
- GitHub Issues: [https://github.com/pinarkive/pinarkive-sdk-py/issues](https://github.com/pinarkive/pinarkive-sdk-py/issues)
- API Documentation: [https://api.pinarkive.com/docs](https://api.pinarkive.com/docs)
- Contact: [https://pinarkive.com/docs.php](https://pinarkive.com/docs.php) 