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

FAKE_CUBES = [
    {
        "Name": "SalesCube",
        "LastSchemaUpdate": "2026-01-15T10:30:00Z",
        "LastDataUpdate": "2026-06-10T08:00:00Z",
    },
    {
        "Name": "BudgetCube",
        "LastSchemaUpdate": "2026-02-01T09:00:00Z",
        "LastDataUpdate": "2026-06-09T07:00:00Z",
    },
]

FAKE_DIMENSIONS = [
    {"Name": "Product", "UniqueName": "[Product]"},
    {"Name": "Region", "UniqueName": "[Region]"},
    {"Name": "Time", "UniqueName": "[Time]"},
]


class FakeIBMPAClient:
    def __init__(self, servers=None, cubes=None, dimensions=None, raise_error=None):
        self._servers = servers if servers is not None else FAKE_SERVERS
        self._cubes = cubes if cubes is not None else FAKE_CUBES
        self._dimensions = dimensions if dimensions is not None else FAKE_DIMENSIONS
        self._raise_error = raise_error  # instance d'exception à lever, ou None
        self.get_servers_call_count = 0
        self.get_cubes_call_count = 0
        self.get_dimensions_call_count = 0
        self.last_cube_server_name = None
        self.last_dimension_server_name = None
        self.last_dimension_cube_name = None

    def get_servers(self):
        self.get_servers_call_count += 1
        if self._raise_error is not None:
            raise self._raise_error
        return list(self._servers)

    def get_cubes(self, server_name):
        self.get_cubes_call_count += 1
        self.last_cube_server_name = server_name
        if self._raise_error is not None:
            raise self._raise_error
        return list(self._cubes)

    def get_dimensions(self, server_name, cube_name):
        self.get_dimensions_call_count += 1
        self.last_dimension_server_name = server_name
        self.last_dimension_cube_name = cube_name
        if self._raise_error is not None:
            raise self._raise_error
        return list(self._dimensions)
