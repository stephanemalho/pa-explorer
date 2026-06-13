from app.clients.ibm_pa import IBMPAAuthError  # noqa: F401 — réexporté pour les tests

FAKE_SERVERS = [
    {
        "Name": "SalesServer",
        "DisplayName": "Sales Server",
        "Host": "sales.example.com",
        "HTTPPort": 8080,
        "IsLocal": False,
        "AcceptingClients": True,
        "Href": "http://sales.example.com:8080",
        "isV12": True,
    },
    {
        "Name": "FinanceServer",
        "DisplayName": "Finance Server",
        "Host": "finance.example.com",
        "HTTPPort": 8081,
        "IsLocal": True,
        "AcceptingClients": False,
        "Href": "http://finance.example.com:8081",
        "isV12": False,
    },
]


class FakeIBMPAClient:
    def __init__(self, servers=None, raise_error=None):
        self._servers = servers if servers is not None else FAKE_SERVERS
        self._raise_error = raise_error  # instance d'exception à lever, ou None
        self.get_servers_call_count = 0

    def get_servers(self):
        self.get_servers_call_count += 1
        if self._raise_error is not None:
            raise self._raise_error
        return list(self._servers)  # copie défensive
