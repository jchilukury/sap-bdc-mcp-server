# SAP Business Data Cloud MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

An MCP (Model Context Protocol) server that provides integration with SAP Business Data Cloud (BDC) Connect SDK. This server enables AI assistants like Claude to interact with SAP BDC for data sharing, Delta Sharing protocol operations, and data product management.

> **Status**: ✅ Released on PyPI - v0.1.0 (2025-12-16)
>
> **New**: ✨ Now supports local development without Databricks notebooks! See [Local Development Setup](#local-development-setup) below.

## Features

This MCP server exposes the following SAP BDC capabilities:

- **Create/Update Shares**: Manage data shares with ORD metadata
- **CSN Schema Management**: Configure shares using Common Semantic Notation
- **Data Product Publishing**: Publish and unpublish data products
- **Share Deletion**: Remove and withdraw shared resources
- **CSN Template Generation**: Auto-generate CSN templates from Databricks shares

## Prerequisites

- Python 3.9+ (Python 3.11+ recommended for local development)
- Access to a Databricks environment
- SAP Business Data Cloud account
- Databricks recipient configured for Delta Sharing
- For local development: Databricks personal access token

## Quick Start

### Installation

Choose your preferred language/platform:

#### Python (PyPI)

```bash
pip install sap-bdc-mcp-server
```

#### Node.js/TypeScript (npm)

```bash
npm install @mariodefelize/sap-bdc-mcp-server
```

**Note:** The npm package requires Python 3.9+ to be installed, as it wraps the Python MCP server.

See [NPM_README.md](NPM_README.md) for full Node.js/TypeScript documentation.

#### From Source

```bash
# Clone the repository
git clone https://github.com/MarioDeFelipe/sap-bdc-mcp-server.git
cd sap-bdc-mcp-server

# Install Python package in development mode
pip install -e .

# Install npm dependencies (optional, for Node.js development)
npm install
```

### Configuration

#### For Local Development (Recommended)

Create a `.env` file in the project root:

```bash
# Databricks Configuration
DATABRICKS_RECIPIENT_NAME=your_recipient_name
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_databricks_token

# Optional
LOG_LEVEL=INFO
```

The server will automatically use `LocalDatabricksClient` which works without `dbutils`.

#### For Databricks Notebook Environment

If running inside Databricks notebooks, only set:

```
DATABRICKS_RECIPIENT_NAME=your_recipient_name
LOG_LEVEL=INFO
```

The server will automatically detect the notebook environment and use `dbutils`.

## Usage

### Python Usage

#### Running the Server

The MCP server runs as a stdio-based service:

```bash
python -m sap_bdc_mcp.server
```

Or using the installed script:

```bash
sap-bdc-mcp
```

#### Integration with Claude Desktop

Add this server to your Claude Desktop configuration file:

**On MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sap-bdc": {
      "command": "python",
      "args": ["-m", "sap_bdc_mcp.server"],
      "env": {
        "DATABRICKS_RECIPIENT_NAME": "your_recipient_name"
      }
    }
  }
}
```

### Node.js/TypeScript Usage

For Node.js/TypeScript applications, use the npm package:

```typescript
import { createSapBdcMcpClient } from '@mariodefelize/sap-bdc-mcp-server';

const client = await createSapBdcMcpClient({
  env: {
    DATABRICKS_HOST: process.env.DATABRICKS_HOST,
    DATABRICKS_TOKEN: process.env.DATABRICKS_TOKEN,
    DATABRICKS_RECIPIENT_NAME: process.env.DATABRICKS_RECIPIENT_NAME,
  },
});

// Validate a share
const validation = await client.validateShareReadiness({
  share_name: 'my_share',
});

console.log(validation);

await client.close();
```

See [NPM_README.md](NPM_README.md) for complete Node.js/TypeScript documentation and examples.

Alternatively, if installed in a virtual environment:

```json
{
  "mcpServers": {
    "sap-bdc": {
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["-m", "sap_bdc_mcp.server"],
      "env": {
        "DATABRICKS_RECIPIENT_NAME": "your_recipient_name"
      }
    }
  }
}
```

## Available Tools

### 1. create_or_update_share

Create or update a data share with ORD metadata.

**Parameters:**
- `share_name` (required): Name of the share
- `ord_metadata` (optional): ORD metadata object
- `tables` (optional): Array of table names to include

**Example:**
```json
{
  "share_name": "customer_data_share",
  "ord_metadata": {
    "title": "Customer Data",
    "description": "Shared customer information"
  },
  "tables": ["customers", "orders"]
}
```

### 2. create_or_update_share_csn

Create or update a share using CSN format.

**Parameters:**
- `share_name` (required): Name of the share
- `csn_schema` (required): CSN schema definition object

**Example:**
```json
{
  "share_name": "product_share",
  "csn_schema": {
    "definitions": {
      "Products": {
        "kind": "entity",
        "elements": {
          "ID": {"type": "String"},
          "name": {"type": "String"}
        }
      }
    }
  }
}
```

### 3. publish_data_product

Publish a data product to make it available for consumption.

**Parameters:**
- `share_name` (required): Name of the share
- `data_product_name` (required): Name of the data product

**Example:**
```json
{
  "share_name": "customer_data_share",
  "data_product_name": "CustomerAnalytics"
}
```

### 4. delete_share

Delete a share and withdraw shared resources.

**Parameters:**
- `share_name` (required): Name of the share to delete

**Example:**
```json
{
  "share_name": "old_share"
}
```

### 5. generate_csn_template

Generate a CSN template from an existing Databricks share.

**Parameters:**
- `share_name` (required): Name of the Databricks share

**Example:**
```json
{
  "share_name": "existing_databricks_share"
}
```

### 6. provision_share ✨ **NEW: End-to-End Orchestration**

**One-step provisioning**: Creates Databricks share, grants to recipient, and registers with SAP BDC in a single operation.

This tool orchestrates the complete workflow:
1. Creates the Databricks Delta share
2. Adds specified tables to the share
3. Grants the share to your configured recipient
4. Registers the share with SAP BDC

**Parameters:**
- `share_name` (required): Name of the share to create
- `tables` (required): Array of table names (format: `catalog.schema.table` or `schema.table`)
- `ord_metadata` (required): ORD metadata object
  - `title` (required): Display title for the share
  - `shortDescription`: Brief description
  - `description`: Detailed description
  - `version`: Version number (e.g., "1.0.0")
  - `releaseStatus`: Status (e.g., "active", "beta")
  - `tags`: Array of tags
- `comment` (optional): Comment for the Databricks share
- `auto_grant` (optional): Auto-grant to recipient (default: `true`)
- `skip_if_exists` (optional): Skip if share already exists (default: `true`)

**Example:**
```json
{
  "share_name": "customer_analytics",
  "tables": ["main.analytics.customers", "main.analytics.orders"],
  "ord_metadata": {
    "title": "Customer Analytics Data",
    "shortDescription": "Customer and order data for analytics",
    "description": "Comprehensive customer analytics dataset including customer profiles and order history",
    "version": "1.0.0",
    "releaseStatus": "active",
    "tags": ["analytics", "customer", "orders"]
  },
  "comment": "Customer analytics share for data consumers",
  "auto_grant": true
}
```

**What it does:**
- ✅ Creates Databricks share (or skips if exists)
- ✅ Adds all specified tables to the share
- ✅ Grants SELECT permission to your recipient
- ✅ Registers with SAP BDC with ORD metadata
- ✅ Provides step-by-step progress feedback
- ✅ If any step fails, shows what completed and what to do manually

**Why use this instead of manual steps:**
- Single command instead of 4 separate operations
- Automatic error handling and recovery guidance
- Idempotent - safe to retry if interrupted
- Clear visibility into each step's success/failure

### 7. validate_share_readiness ✨ **NEW: Pre-flight Validation**

**Validate before you register**: Check if a Databricks share is ready for BDC Connect operations.

This tool performs comprehensive pre-flight checks:
1. ✅ Verifies the share exists in Databricks
2. ✅ Checks if the share has tables/objects
3. ✅ Validates the share is granted to your recipient
4. ✅ Provides actionable next steps if validation fails

**Parameters:**
- `share_name` (required): Name of the share to validate
- `check_bdc_registration` (optional): Also check BDC registration status (default: `false`)

**Example:**
```json
{
  "share_name": "customer_data_share"
}
```

**Success Response:**
```
✅ Share 'customer_data_share' is READY for BDC Connect registration!

All checks passed:
  ✅ PASS Share 'customer_data_share' exists in Databricks
  ✅ PASS Share has 3 object(s)
  ✅ PASS Share is granted to recipient 'bdc-connect-12345'

Next step: Register with BDC using create_or_update_share('customer_data_share', ...)
```

**Failure Response:**
```
❌ Share 'test_share' is NOT ready for BDC Connect

Errors found:
  ❌ Share is empty - no tables added
  ❌ Share not granted to BDC Connect recipient 'bdc-connect-12345'

Required actions:
  1. Add tables: w.shares.update(name='test_share', ...)
  2. Grant share: GRANT SELECT ON SHARE test_share TO RECIPIENT `bdc-connect-12345`
```

**Use Cases:**
- **Before registration**: Validate a share before calling `create_or_update_share`
- **Troubleshooting**: Understand why registration failed
- **Documentation**: Generate a checklist of what's needed
- **CI/CD pipelines**: Automated validation before deployment
- **Onboarding**: Help new users understand the prerequisites

**Why this matters:**
- Prevents "trial and error" workflow - know upfront if share is ready
- Clear, actionable guidance instead of cryptic error messages
- Saves time by catching issues before attempting registration
- Validates all prerequisites in one call

## Architecture

The server uses:
- **MCP SDK**: For protocol implementation
- **SAP BDC Connect SDK**: For SAP Business Data Cloud operations
- **Delta Sharing**: Open protocol for secure data sharing
- **ORD Protocol**: For resource discovery and metadata

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
sap-bdc-mcp-server/
├── src/
│   └── sap_bdc_mcp/
│       ├── __init__.py
│       ├── server.py       # Main MCP server implementation
│       └── config.py       # Configuration management
├── pyproject.toml          # Project dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

## Local Development Setup

### The `dbutils` Challenge

The SAP BDC Connect SDK was originally designed to run inside Databricks notebooks, requiring access to `dbutils` (Databricks utilities). This made local development challenging.

### Our Solution: LocalDatabricksClient

We've created `LocalDatabricksClient` - a custom wrapper that extends the SAP BDC SDK to work **without** `dbutils`. This enables:

✅ **Local development** - Run on your machine without Databricks notebooks
✅ **IDE integration** - Use your favorite development tools
✅ **Easier debugging** - Standard Python debugging workflows
✅ **CI/CD friendly** - Works in automated pipelines
✅ **Claude Desktop integration** - Direct MCP server usage

### How It Works

The `LocalDatabricksClient` class:

1. **Bypasses `dbutils` requirement** - Accepts workspace URL and API token directly
2. **Reads from `.env` file** - No notebook context needed
3. **Auto-detects mode** - Automatically uses brownfield (BDC Connect) or Databricks Connect mode
4. **Maintains compatibility** - Fully compatible with the SAP BDC SDK API
5. **Clear error messages** - Helpful guidance if configuration is missing

```python
from sap_bdc_mcp.local_client import LocalDatabricksClient

# Initialize from environment variables
client = LocalDatabricksClient.from_env()

# Or with explicit credentials
client = LocalDatabricksClient(
    workspace_url="https://your-workspace.cloud.databricks.com",
    api_token="your_token",
    recipient_name="your_recipient"
)
```

### Two Modes Supported

**BDC Connect Mode (Brownfield)** ✨
- Uses OIDC federation for authentication
- No Databricks secrets required
- Simpler setup
- Automatically detected if recipient is configured

**Databricks Connect Mode**
- Requires additional secrets (api_url, tenant, token_audience)
- Can be provided via environment variables
- For greenfield deployments

### Setup Guide

See our comprehensive guides:
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[IMPLEMENTATION_SUCCESS.md](IMPLEMENTATION_SUCCESS.md)** - Technical deep dive
- **[HOW_TO_CREATE_SHARE.md](HOW_TO_CREATE_SHARE.md)** - Complete workflow guide

### For Blog Posts / Technical Articles

Key points to highlight:

1. **The Problem**: SAP BDC SDK requires `dbutils`, limiting usage to Databricks notebooks
2. **The Investigation**: We analyzed the SDK to understand what `dbutils` actually provided
3. **The Discovery**: Only 2 uses - getting workspace credentials and accessing secrets
4. **The Solution**: Created `LocalDatabricksClient` that injects credentials directly
5. **The Result**: Full local development support with < 200 lines of code

**Technical highlights:**
- Custom inheritance from `DatabricksClient`
- Override `__init__` to bypass `dbutils` requirement
- Override `_get_secret()` to read from env vars
- Maintains all SDK functionality
- Zero changes to SAP BDC SDK itself

## Architecture

### System Overview

```
┌─────────────────────────┐
│   Claude Desktop        │
│   (MCP Client)          │
└───────────┬─────────────┘
            │ MCP Protocol (stdio)
┌───────────▼─────────────┐
│  sap_bdc_mcp.server     │
│  ┌───────────────────┐  │
│  │ BDCClientManager  │  │
│  │   (Auto-detect)   │  │
│  └────────┬──────────┘  │
│           ├─────────────┼─ Notebook? → DatabricksClient (dbutils)
│           │             │
│           └─────────────┼─ Local? → LocalDatabricksClient (.env)
└───────────┼─────────────┘
            │
┌───────────▼─────────────┐
│ SAP BDC Connect SDK     │
│ ┌──────────────────┐    │
│ │ BdcConnectClient │    │
│ └────────┬─────────┘    │
└──────────┼──────────────┘
           │ HTTPS/OIDC
┌──────────▼──────────────┐
│  Databricks + SAP BDC   │
└─────────────────────────┘
```

### Traditional Architecture

The server uses:
- **MCP SDK**: For protocol implementation
- **SAP BDC Connect SDK**: For SAP Business Data Cloud operations
- **Delta Sharing**: Open protocol for secure data sharing
- **ORD Protocol**: For resource discovery and metadata

## Important Notes

### Databricks Integration

The server supports two integration modes:

**1. Notebook Mode** (Original)
- Runs inside Databricks notebooks
- Uses `dbutils` for credentials
- Requires active notebook session

**2. Local Mode** (New!) ✨
- Runs on your local machine
- Uses environment variables for credentials
- No notebook required

### Authentication

Authentication is handled through:
1. Databricks workspace credentials (URL + token)
2. Recipient configuration in Databricks
3. SAP BDC service credentials (auto-configured in BDC Connect mode)

## Troubleshooting

### "BDC client not initialized" Error

**For Local Development:**
- Ensure `.env` file exists with `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and `DATABRICKS_RECIPIENT_NAME`
- Check that your Databricks token is valid
- Verify the workspace URL is correct

**For Notebook Environment:**
- Ensure you're running in a Databricks notebook with `dbutils` available
- Set `DATABRICKS_RECIPIENT_NAME` environment variable

### Missing Environment Variables

For local development, ensure these are set in your `.env` file:
```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_RECIPIENT_NAME=your_recipient_name
```

### "Share does not exist" Error

The share must exist in Databricks before registering with SAP BDC:
1. Create a Delta share in Databricks first
2. Grant the share to your recipient
3. Then register it with SAP BDC using this server

See [HOW_TO_CREATE_SHARE.md](HOW_TO_CREATE_SHARE.md) for detailed steps.

### "Permission denied" or "Share not granted to recipient"

Grant the share to your recipient in Databricks:
```sql
GRANT SELECT ON SHARE your_share_name TO RECIPIENT `your_recipient_name`;
```

## Resources

- [SAP BDC Connect SDK on PyPI](https://pypi.org/project/sap-bdc-connect-sdk/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Delta Sharing Protocol](https://delta.io/sharing/)
- [SAP Business Data Cloud](https://www.sap.com)

## License

This MCP server is provided as-is. Please review the SAP BDC Connect SDK license terms when using this integration.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Setting up your development environment
- Running tests
- Submitting pull requests
- Code style guidelines

## Roadmap

- [x] Initial validation with Databricks environment
- [x] Local development support (LocalDatabricksClient)
- [x] PyPI package publication
- [x] Comprehensive documentation
- [ ] npm package for Node.js environments
- [ ] Additional SAP BDC SDK features
- [ ] Enhanced error handling and logging
- [ ] More integration examples and tutorials
- [ ] Video tutorials and demos

## Support

- **Issues**: [GitHub Issues](https://github.com/MarioDeFelipe/sap-bdc-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MarioDeFelipe/sap-bdc-mcp-server/discussions)
- **Documentation**: [Wiki](https://github.com/MarioDeFelipe/sap-bdc-mcp-server/wiki)

## Acknowledgments

- SAP for the BDC Connect SDK
- Anthropic for the Model Context Protocol
- The MCP community for inspiration and support
