# Pinarkive Python SDK

Minimal Python client for the **PinArkive API v3**. Upload files, pin by CID, manage tokens, and check status. See [pinarkive.com/docs.php](https://pinarkive.com/docs.php).

**Version:** 3.0.1

## Installation

```bash
pip install pinarkive-sdk-py
```

## Quick Start

```python
from pinarkive_client import PinarkiveClient, PinarkiveError

# Auth: Bearer token or X-API-Key (default base URL: https://api.pinarkive.com/api/v3)
client = PinarkiveClient(api_key="your-api-key-here")

# Upload a file
result = client.upload_file("document.pdf")
print(result["cid"])

# Or login first
login = client.login("user@example.com", "password")
client = PinarkiveClient(token=login["token"])

# List uploads
data = client.list_uploads(page=1, limit=20)
print(data["uploads"])
```

## Authentication

- **API Key:** `PinarkiveClient(api_key="...")` — sent as `X-API-Key` header.
- **JWT:** `PinarkiveClient(token="...")` — sent as `Authorization: Bearer <token>`.
- **Base URL:** optional third argument, default `https://api.pinarkive.com/api/v3`.

## API Methods (minimal set)

| Method | Description |
|--------|-------------|
| `health()` | GET /health |
| `get_plans()` | GET /plans/ |
| `get_peers()` | GET /peers/ |
| `login(email, password)` | POST /auth/login |
| `upload_file(path, cluster_id=None, timelock=None)` | POST /files/ |
| `upload_directory(dir_path, cluster_id=None, timelock=None)` | POST /files/directory |
| `upload_directory_dag(files_dict, dir_name=None, cluster_id=None, timelock=None)` | POST /files/directory-dag |
| `pin_cid(cid, original_name=None, custom_name=None, cluster_id=None, timelock=None)` | POST /files/pin/:cid |
| `remove_file(cid)` | DELETE /files/remove/:cid |
| `get_me()` | GET /users/me |
| `list_uploads(page=1, limit=20)` | GET /users/me/uploads |
| `generate_token(name, label=None, expires_in_days=None)` | POST /tokens/generate |
| `list_tokens()` | GET /tokens/list |
| `revoke_token(name)` | DELETE /tokens/revoke/:name |
| `get_status(cid, cluster_id=None)` | GET /status/:cid |
| `get_allocations(cid, cluster_id=None)` | GET /allocations/:cid |

Optional `cluster_id` and `timelock` (ISO 8601, premium) follow the API docs.

## Error handling

On HTTP 4xx/5xx the client raises **`PinarkiveError`** with:

- `status_code` — HTTP status (400, 401, 403, 404, 409, 413, 429, 500, 503)
- `message` — from API `message` or `error`
- `body` — full JSON body
- `.error` — API field `error`
- `.code` — API field `code` (e.g. `email_not_verified`)

```python
try:
    client.upload_file("large.bin")
except PinarkiveError as e:
    print(e.status_code, e.message, e.code)
```

## Changelog

### 3.0.0

- **API v3:** Base URL is now `https://api.pinarkive.com/api/v3` (was `/api/v2`). v1/v2 are deprecated (410).
- **Errors:** On 4xx/5xx the client raises `PinarkiveError` with `status_code`, `message`, `body`, and `.error` / `.code` from the API (no raw `Response` on failure).
- **Minimal surface:** Only endpoints documented at [pinarkive.com/docs.php](https://pinarkive.com/docs.php): health, plans, peers, login, files (upload, directory, directory-dag, pin, remove), users/me, uploads, tokens (generate with `name` / `label` / `expiresInDays`), status, allocations. Optional `cluster_id` and `timelock` (ISO 8601) on upload/pin.
- **Removed:** `rename_file`; token options `permissions`, `ip_allowlist`. Use API `label` and `expiresInDays` only.
- **Pin:** `pin_cid` now accepts `original_name`, `custom_name` (replacing the old `filename`).
- **Return values:** Successful calls return decoded JSON (dict); methods that return nothing on success (`remove_file`, `revoke_token`) return `None`.

### Upgrading from 2.x

1. Change base URL to `/api/v3` or rely on the new default.
2. Replace `result.json()` with the direct return value (client returns dicts; on error, `PinarkiveError` is raised).
3. Catch `PinarkiveError` instead of `requests.HTTPError` and use `e.status_code`, `e.message`, `e.body`.
4. Use `pin_cid(cid, custom_name=...)` instead of `pin_cid(cid, filename=...)`; add `original_name` if needed.
5. Use `generate_token(name, label=..., expires_in_days=...)`; drop `permissions` and `ip_allowlist`.
6. Pin to `pinarkive-sdk-py>=3.0.0` if you rely on v3 behaviour.

## Links

- [API docs](https://pinarkive.com/docs.php)
- [Repository](https://github.com/pinarkive/pinarkive-sdk-py)
