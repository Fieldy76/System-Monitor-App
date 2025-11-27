# Agent Setup Guide

The System Monitor App supports monitoring multiple servers via a central dashboard. This guide explains how to set up the application in "Agent Mode" on remote servers.

## Prerequisites

- Python 3.11+
- Network connectivity to the central dashboard server
- API Key from the central dashboard

## Step 1: Generate API Key

1. Log in to the central System Monitor dashboard as an Admin.
2. Go to the **Servers** page.
3. Click "Add Server".
4. Enter the Name and Hostname/IP of the remote server.
5. Copy the generated **API Key**.

## Step 2: Install Agent

On the remote server you want to monitor:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd "System Monitor App"
   ```

2. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Configure `.env` for Agent Mode:
   Edit the `.env` file and set the following:
   ```bash
   # Agent Configuration
   AGENT_MODE=true
   CENTRAL_SERVER_URL=http://<central-dashboard-ip>:5000
   AGENT_API_KEY=<your-api-key-from-step-1>
   ```

   *Note: Ensure `AGENT_MODE` is implemented in `config.py` if not already present, or simply run the app and ensure the API endpoints are accessible.*

## Step 3: Run the Agent

Start the application:

```bash
python run.py
```

The agent will now expose the `/api/metrics` endpoint which the central server will poll.

## Verification

1. Go back to the central dashboard **Servers** page.
2. The new server should show as "Active" with a recent "Last Seen" timestamp.
3. You can now select this server from the dashboard dropdown to view its metrics.

## Troubleshooting

- **Connection Refused**: Ensure the agent server's firewall allows incoming connections on port 5000 (or your configured port).
- **Authentication Failed**: Verify the API Key matches exactly.
- **No Data**: Check the agent logs for errors.
