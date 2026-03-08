"""
Pinarkive SDK Python – API v3.
Minimal client for https://pinarkive.com/docs.php (upload, pin, remove, users/me, uploads, tokens, status, allocations).
Errors raise PinarkiveError with status_code and API body (error, message, code) per API v3 HTTP codes.
"""

__version__ = "3.0.0"

import io
import os
from typing import Optional, Dict, Any, Union, BinaryIO

import requests


class PinarkiveError(Exception):
    """
    Raised when the API returns HTTP 4xx or 5xx.
    Attributes: status_code (int), message (str), body (dict with error, message, code from API).
    API v3 codes: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found,
    409 Conflict, 413 Payload Too Large, 429 Too Many Requests, 500 Internal Server Error, 503 Service Unavailable.
    """

    def __init__(self, status_code: int, message: str, body: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.message = message
        self.body = body or {}
        super().__init__(f"[{status_code}] {message}")

    @property
    def error(self) -> str:
        """API field 'error'."""
        return self.body.get("error", "")

    @property
    def code(self) -> str:
        """API field 'code' (e.g. email_not_verified, account_disabled)."""
        return self.body.get("code", "")


class PinarkiveClient:
    """Client for PinArkive API v3. Auth: Bearer token or X-API-Key."""

    def __init__(
        self,
        token: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.pinarkive.com/api/v3",
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.api_key = api_key
        self.session = requests.Session()

    def _headers(self, auth: bool = True) -> Dict[str, str]:
        headers = {}
        if auth:
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            elif self.api_key:
                headers["X-API-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        auth: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        kwargs.setdefault("headers", {}).update(self._headers(auth=auth))
        r = self.session.request(method, url, **kwargs)
        if not r.ok:
            body = {}
            msg = f"Request failed ({r.status_code})"
            ct = r.headers.get("Content-Type", "")
            if "application/json" in ct:
                try:
                    body = r.json()
                    msg = body.get("message") or body.get("error") or msg
                except Exception:
                    pass
            raise PinarkiveError(r.status_code, msg, body)
        return r

    # --- Public (no auth) ---
    def health(self) -> Any:
        """GET /health"""
        return self._request("GET", "/health", auth=False).json()

    def get_plans(self) -> Any:
        """GET /plans/"""
        return self._request("GET", "/plans/", auth=False).json()

    def get_peers(self) -> Any:
        """GET /peers/"""
        return self._request("GET", "/peers/", auth=False).json()

    def login(self, email: str, password: str) -> Any:
        """POST /auth/login. Returns { token, user? }."""
        return self._request(
            "POST", "/auth/login", auth=False, json={"email": email, "password": password}
        ).json()

    # --- Files ---
    def upload_file(
        self,
        file_path: Union[str, os.PathLike],
        cluster_id: Optional[str] = None,
        timelock: Optional[str] = None,
    ) -> Any:
        """POST /files/ – multipart file, optional cl, timelock (ISO 8601, premium)."""
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {}
            if cluster_id:
                data["cl"] = cluster_id
            if timelock:
                data["timelock"] = timelock
            return self._request("POST", "/files/", files=files, data=data or None).json()

    def upload_directory(
        self,
        dir_path: str,
        cluster_id: Optional[str] = None,
        timelock: Optional[str] = None,
    ) -> Any:
        """POST /files/directory – body dirPath, optional cl, timelock."""
        body = {"dirPath": dir_path}
        if cluster_id:
            body["cl"] = cluster_id
        if timelock:
            body["timelock"] = timelock
        return self._request("POST", "/files/directory", json=body).json()

    def upload_directory_dag(
        self,
        files_dict: Dict[str, Any],
        dir_name: Optional[str] = None,
        cluster_id: Optional[str] = None,
        timelock: Optional[str] = None,
    ) -> Any:
        """POST /files/directory-dag – multipart files[i][path], files[i][content]; optional cl, timelock."""
        files = []
        for i, (path, content) in enumerate(files_dict.items()):
            files.append((f"files[{i}][path]", path))
            if hasattr(content, "read"):
                fileobj = content
                files.append((f"files[{i}][content]", (os.path.basename(path), fileobj, "application/octet-stream")))
            elif isinstance(content, bytes):
                files.append((f"files[{i}][content]", (os.path.basename(path), io.BytesIO(content), "application/octet-stream")))
            else:
                files.append((f"files[{i}][content]", (os.path.basename(path), io.BytesIO(str(content).encode("utf-8")), "text/plain")))
        data = {}
        if dir_name:
            data["dirName"] = dir_name
        if cluster_id:
            data["cl"] = cluster_id
        if timelock:
            data["timelock"] = timelock
        return self._request("POST", "/files/directory-dag", files=files, data=data or None).json()

    def pin_cid(
        self,
        cid: str,
        original_name: Optional[str] = None,
        custom_name: Optional[str] = None,
        cluster_id: Optional[str] = None,
        timelock: Optional[str] = None,
    ) -> Any:
        """POST /files/pin/:cid – optional originalName, customName, cl, timelock."""
        body = {}
        if original_name is not None:
            body["originalName"] = original_name
        if custom_name is not None:
            body["customName"] = custom_name
        if cluster_id:
            body["cl"] = cluster_id
        if timelock:
            body["timelock"] = timelock
        return self._request("POST", f"/files/pin/{cid}", json=body).json()

    def remove_file(self, cid: str) -> None:
        """DELETE /files/remove/:cid"""
        self._request("DELETE", f"/files/remove/{cid}")

    # --- Users ---
    def get_me(self) -> Any:
        """GET /users/me"""
        return self._request("GET", "/users/me").json()

    def list_uploads(self, page: int = 1, limit: int = 20) -> Any:
        """GET /users/me/uploads?page=&limit="""
        return self._request(
            "GET", "/users/me/uploads", params={"page": page, "limit": limit}
        ).json()

    # --- Tokens (name required; label default cli-access; expiresInDays optional) ---
    def generate_token(
        self,
        name: str,
        label: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Any:
        """POST /tokens/generate – name required, optional label (default cli-access), expiresInDays."""
        body = {"name": name}
        if label is not None:
            body["label"] = label
        if expires_in_days is not None:
            body["expiresInDays"] = expires_in_days
        return self._request("POST", "/tokens/generate", json=body).json()

    def list_tokens(self) -> Any:
        """GET /tokens/list"""
        return self._request("GET", "/tokens/list").json()

    def revoke_token(self, name: str) -> None:
        """DELETE /tokens/revoke/:name"""
        self._request("DELETE", f"/tokens/revoke/{name}")

    # --- Status ---
    def get_status(self, cid: str, cluster_id: Optional[str] = None) -> Any:
        """GET /status/:cid?cl= (optional cluster id)."""
        params = {"cl": cluster_id} if cluster_id else None
        return self._request("GET", f"/status/{cid}", params=params).json()

    def get_allocations(self, cid: str, cluster_id: Optional[str] = None) -> Any:
        """GET /allocations/:cid?cl="""
        params = {"cl": cluster_id} if cluster_id else None
        return self._request("GET", f"/allocations/{cid}", params=params).json()
