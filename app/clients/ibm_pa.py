import urllib.parse

import httpx


class IBMPAError(Exception):
    pass


class IBMPAAuthError(IBMPAError):
    pass


class IBMPAForbiddenError(IBMPAError):
    pass


class IBMPATimeoutError(IBMPAError):
    pass


class IBMPAConnectionError(IBMPAError):
    pass


class IBMPAServerError(IBMPAError):
    def __init__(self, status_code: int, body: str = "") -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"IBM PA server error {status_code}")


class IBMPAUnexpectedResponseError(IBMPAError):
    pass


class IBMPAClient:
    _SERVERS_PATH = "/api/{tenant_id}/v0/tm1/Servers"
    _CUBES_PATH = "/api/{tenant_id}/v0/tm1/{server_name}/Cubes"
    _DIMENSIONS_PATH = "/api/{tenant_id}/v0/tm1/{server_name}/Cubes('{cube_name}')/Dimensions"

    def __init__(self, base_url: str, tenant_id: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._tenant_id = tenant_id
        self._auth = httpx.BasicAuth("apikey", api_key)

    def _url(self, path: str, **kwargs) -> str:
        return f"{self._base_url}{path.format(tenant_id=self._tenant_id, **kwargs)}"

    def get_cubes(self, server_name: str) -> list[dict]:
        url = self._url(self._CUBES_PATH, server_name=server_name)
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    url,
                    auth=self._auth,
                    headers={"Accept": "application/json"},
                )
        except httpx.TimeoutException as exc:
            raise IBMPATimeoutError(str(exc)) from exc
        except httpx.ConnectError as exc:
            raise IBMPAConnectionError(str(exc)) from exc

        if response.status_code == 401:
            raise IBMPAAuthError("IBM PA returned 401 Unauthorized")
        if response.status_code == 403:
            raise IBMPAForbiddenError("IBM PA returned 403 Forbidden")
        if response.status_code >= 500:
            raise IBMPAServerError(response.status_code, response.text[:500])
        if not response.is_success:
            raise IBMPAUnexpectedResponseError(f"Unexpected HTTP {response.status_code}: {response.text[:200]}")

        try:
            data = response.json()
        except Exception as exc:
            raise IBMPAUnexpectedResponseError("IBM PA response is not valid JSON") from exc

        try:
            return data.get("value", [])
        except AttributeError as exc:
            raise IBMPAUnexpectedResponseError("IBM PA response has unexpected structure") from exc

    def get_dimensions(self, server_name: str, cube_name: str) -> list[dict]:
        encoded_cube = urllib.parse.quote(cube_name, safe="")
        url = self._url(self._DIMENSIONS_PATH, server_name=server_name, cube_name=encoded_cube)
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    url,
                    auth=self._auth,
                    headers={"Accept": "application/json"},
                )
        except httpx.TimeoutException as exc:
            raise IBMPATimeoutError(str(exc)) from exc
        except httpx.ConnectError as exc:
            raise IBMPAConnectionError(str(exc)) from exc

        if response.status_code == 401:
            raise IBMPAAuthError("IBM PA returned 401 Unauthorized")
        if response.status_code == 403:
            raise IBMPAForbiddenError("IBM PA returned 403 Forbidden")
        if response.status_code >= 500:
            raise IBMPAServerError(response.status_code, response.text[:500])
        if not response.is_success:
            raise IBMPAUnexpectedResponseError(f"Unexpected HTTP {response.status_code}: {response.text[:200]}")

        try:
            data = response.json()
        except Exception as exc:
            raise IBMPAUnexpectedResponseError("IBM PA response is not valid JSON") from exc

        try:
            return data.get("value", [])
        except AttributeError as exc:
            raise IBMPAUnexpectedResponseError("IBM PA response has unexpected structure") from exc

    def get_servers(self) -> list[dict]:
        url = self._url(self._SERVERS_PATH)
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    url,
                    auth=self._auth,
                    headers={"Accept": "application/json"},
                )
        except httpx.TimeoutException as exc:
            raise IBMPATimeoutError(str(exc)) from exc
        except httpx.ConnectError as exc:
            raise IBMPAConnectionError(str(exc)) from exc

        if response.status_code == 401:
            raise IBMPAAuthError("IBM PA returned 401 Unauthorized")
        if response.status_code == 403:
            raise IBMPAForbiddenError("IBM PA returned 403 Forbidden")
        if response.status_code >= 500:
            raise IBMPAServerError(response.status_code, response.text[:500])
        if not response.is_success:
            raise IBMPAUnexpectedResponseError(f"Unexpected HTTP {response.status_code}: {response.text[:200]}")

        try:
            data = response.json()
        except Exception as exc:
            raise IBMPAUnexpectedResponseError("IBM PA response is not valid JSON") from exc

        try:
            return data.get("value", [])
        except AttributeError as exc:
            raise IBMPAUnexpectedResponseError("IBM PA response has unexpected structure") from exc
