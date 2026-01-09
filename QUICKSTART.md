# Quick Start Guide - SAP BDC MCP Server

## ✅ Setup Complete!

Your SAP BDC MCP Server is ready to use with Python 3.11 and local development support.

## Activate Your Environment

```bash
cd c:\Users\mariodefe\sap-bdc-mcp-server
.\venv-py311\Scripts\activate
```

## Test the Server

```bash
python -m sap_bdc_mcp.server
```

You should see:
```
INFO:root:Loaded environment from C:\Users\mariodefe\sap-bdc-mcp-server\.env
INFO:sap-bdc-mcp:Starting SAP BDC MCP Server...
INFO:sap-bdc-mcp:Initializing from environment variables
INFO:sap-bdc-mcp:SAP BDC clients initialized successfully
INFO:sap-bdc-mcp:BDC client manager initialized successfully
```

Press `Ctrl+C` to stop.

## Integrate with Claude Desktop

1. **Open Claude Desktop config:**
   - Press `Win+R`, type: `%APPDATA%\Claude`
   - Create or edit `claude_desktop_config.json`

2. **Add this configuration:**

```json
{
  "mcpServers": {
    "sap-bdc": {
      "command": "C:\\Users\\mariodefe\\sap-bdc-mcp-server\\venv-py311\\Scripts\\python.exe",
      "args": ["-m", "sap_bdc_mcp.server"]
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test it** - Ask Claude:
   ```
   "What SAP BDC tools do you have available?"
   ```

## Available Tools

Once integrated, you can ask Claude to:

- **Create shares**: "Create a new share called 'customer_data' in SAP BDC"
- **Update shares**: "Add tables to the 'sales_data' share"
- **Publish data products**: "Publish the 'analytics' share as a data product"
- **Generate CSN templates**: "Generate a CSN template for the 'inventory' share"
- **Delete shares**: "Delete the 'old_test' share"

## Your Configuration

**Mode**: BDC Connect (Brownfield) ✅
- No Databricks secrets required
- OIDC authentication via recipient
- Ready to use immediately

**Credentials**: Loaded from `.env`
- Workspace: `https://dbc-a413df6c-f111.cloud.databricks.com`
- Recipient: `bdc-connect-35c0d016`
- Authentication: Via Databricks token

## Troubleshooting

### Server won't start?
```bash
# Check if environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv('.env'); import os; print('Token set:', bool(os.getenv('DATABRICKS_TOKEN')))"
```

### Claude can't connect?
- Verify the path in `claude_desktop_config.json` is correct
- Restart Claude Desktop completely
- Check Claude Desktop logs (Help → View Logs)

### Want to test without Claude?
```bash
python -c "from sap_bdc_mcp.server import client_manager; client_manager.initialize(); print('Success!')"
```

## Documentation

- [IMPLEMENTATION_SUCCESS.md](IMPLEMENTATION_SUCCESS.md) - Complete implementation details
- [SETUP_STATUS.md](SETUP_STATUS.md) - Setup history and configuration
- [README.md](README.md) - Original project documentation

## Get Help

- Check the logs when the server runs
- Read error messages - they're designed to be helpful
- Review [IMPLEMENTATION_SUCCESS.md](IMPLEMENTATION_SUCCESS.md) for architecture details

## What's Next?

1. Try creating a real share in SAP BDC
2. Explore the CSN template generation
3. Integrate with your data workflows
4. Share feedback or contribute improvements!

---

**You're all set!** The server is running in **BDC Connect mode** and ready to use. 🚀
