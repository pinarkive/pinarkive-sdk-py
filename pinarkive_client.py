import requests
from typing import Optional, Dict, Any, List, Union, BinaryIO
import os

class PinarkiveClient:
    def __init__(self, token: Optional[str] = None, api_key: Optional[str] = None, base_url: str = 'https://api.pinarkive.com/api/v2'):
        self.base_url = base_url
        self.token = token
        self.api_key = api_key
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        elif self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers


    # --- File Management ---
    def uploadFile(self, file_path: str) -> Any:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.session.post(
                f'{self.base_url}/files',
                files=files,
                headers=self._headers()
            )

    def uploadDirectory(self, dir_path: str) -> Any:
        return self.session.post(
            f'{self.base_url}/files/directory',
            json={'dirPath': dir_path},
            headers=self._headers()
        )

    # New: Directory DAG upload
    def uploadDirectoryDAG(self, files_dict: Dict[str, Any], dir_name: Optional[str] = None) -> Any:
        """
        Upload directory structure as DAG (Directed Acyclic Graph).
        
        Args:
            files_dict: Dictionary with file paths as keys and file content as values
            dir_name: Optional directory name for the DAG
        
        Returns:
            API response with DAG CID and file information
        """
        files = []
        for path, content in files_dict.items():
            if isinstance(content, str):
                # If content is a string, treat it as file content
                files.append(('files', (path, content, 'text/plain')))
            elif isinstance(content, (bytes, BinaryIO)):
                # If content is bytes or file-like object
                files.append(('files', (path, content, 'application/octet-stream')))
            else:
                # Try to convert to string
                files.append(('files', (path, str(content), 'text/plain')))
        
        data = {}
        if dir_name:
            data['dirName'] = dir_name
        
        return self.session.post(
            f'{self.base_url}/files/directory-dag',
            files=files,
            data=data,
            headers=self._headers()
        )

    # New: Rename file
    def renameFile(self, upload_id: str, new_name: str) -> Any:
        """
        Rename an uploaded file.
        
        Args:
            upload_id: ID of the uploaded file
            new_name: New name for the file
        
        Returns:
            API response with rename status
        """
        return self.session.put(
            f'{self.base_url}/files/rename/{upload_id}',
            json={'newName': new_name},
            headers=self._headers()
        )

    def pinCid(self, cid: str, filename: Optional[str] = None) -> Any:
        payload = {}
        if filename:
            payload['filename'] = filename
        return self.session.post(
            f'{self.base_url}/files/pin/{cid}',
            json=payload,
            headers=self._headers()
        )


    def removeFile(self, cid: str) -> Any:
        return self.session.delete(
            f'{self.base_url}/files/remove/{cid}',
            headers=self._headers()
        )

    def listUploads(self, page: int = 1, limit: int = 10) -> Any:
        return self.session.get(
            f'{self.base_url}/users/me/uploads',
            params={'page': page, 'limit': limit},
            headers=self._headers()
        )

    # --- Token Management ---
    def generateToken(self, name: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """
        Generate an API token with enhanced options.
        
        Args:
            name: Name for the token
            options: Optional dictionary with:
                - permissions: List of permissions
                - expires_in_days: Number of days until expiration
                - ip_allowlist: List of allowed IP addresses
        
        Returns:
            API response with token information
        """
        data = {'name': name}
        
        if options:
            if 'permissions' in options:
                data['permissions'] = options['permissions']
            if 'expires_in_days' in options:
                data['expiresInDays'] = options['expires_in_days']
            if 'ip_allowlist' in options:
                data['ipAllowlist'] = options['ip_allowlist']
        
        return self.session.post(
            f'{self.base_url}/tokens/generate',
            json=data,
            headers=self._headers()
        )

    def listTokens(self) -> Any:
        return self.session.get(
            f'{self.base_url}/tokens/list',
            headers=self._headers()
        )

    def revokeToken(self, name: str) -> Any:
        return self.session.delete(
            f'{self.base_url}/tokens/revoke/{name}',
            headers=self._headers()
        )

    # --- Status and Monitoring ---
    def getStatus(self, cid: str) -> Any:
        return self.session.get(
            f'{self.base_url}/status/{cid}',
            headers=self._headers()
        )

    def getAllocations(self, cid: str) -> Any:
        return self.session.get(
            f'{self.base_url}/status/allocations/{cid}',
            headers=self._headers()
        )