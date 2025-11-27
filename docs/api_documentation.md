# System Monitor API Documentation

## Authentication

All API endpoints (except login/register) require authentication. The application uses session-based authentication for browser access and API Key authentication for server-to-server communication.

### Session Authentication
Standard Flask-Login session management. Authenticate via the login page or `/auth/login` endpoint.

### API Key Authentication
For agent communication, provide the API key in the header:
`X-API-Key: <your-api-key>`

## Endpoints

### Metrics

#### `GET /api/metrics`
Retrieve real-time system metrics.

**Parameters:**
- `server_id` (optional): ID of the server to fetch metrics for. Defaults to local server.

**Response:**
```json
{
  "cpu": { "percent": 45.2, "freq": "2400.00Mhz", "temp_c": 55.0, "temp_f": 131.0 },
  "memory": { "total": "16.00GB", "used": "7.50GB", "percent": 46.9 },
  "disk": [ ... ],
  "io": { ... },
  "network": { ... },
  "connections": { ... }
}
```

### Network

#### `GET /api/network/connections`
Get detailed network connection information.

**Parameters:**
- `status` (optional): Filter by connection status (e.g., `ESTABLISHED`, `LISTEN`).

**Response:**
```json
{
  "connections": [
    {
      "protocol": "TCP",
      "local_address": "192.168.1.100:5000",
      "remote_address": "93.184.216.34:443",
      "status": "ESTABLISHED",
      "pid": 1234,
      "process": "chrome"
    }
  ],
  "count": 1
}
```

### Disk I/O

#### `GET /api/disk/io-processes`
Get processes sorted by I/O activity.

**Parameters:**
- `sort` (optional): Sort field. Values: `read`, `write`, `total` (default).

**Response:**
```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "chrome",
      "read_bytes": 1024,
      "write_bytes": 2048,
      "read_count": 10,
      "write_count": 20
    }
  ],
  "count": 1
}
```

#### `GET /api/disk/analyze`
Analyze disk usage for a specific mountpoint.

**Parameters:**
- `mountpoint` (optional): The mountpoint to analyze (default: `/`).

### Historical Data

#### `GET /api/metrics/history`
Get historical metrics data.

**Parameters:**
- `server_id` (optional): Server ID.
- `hours` (optional): Number of hours of history (default: 24).
- `type` (optional): Metric type (`system` or `network`).

### Processes

#### `GET /api/processes`
Get list of running processes.

#### `GET /api/processes/<pid>`
Get details for a specific process.

#### `POST /api/processes/<pid>/kill`
Terminate a process (Admin only).

### Alerts

#### `GET /api/alerts/rules`
Get all alert rules.

#### `POST /api/alerts/rules`
Create a new alert rule.

#### `GET /api/alerts/history`
Get alert history.

### Servers

#### `GET /api/servers`
Get list of all servers.

#### `POST /api/servers`
Register a new server (Admin only).
