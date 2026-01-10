# Deploying SAP BDC Tools in Databricks

## Understanding the Architecture

The SAP BDC MCP Server has **two distinct use cases**:

### 1. **MCP Server (Local Development)**
- Runs on your **local machine** (laptop, desktop)
- Integrates with **Claude Desktop** or other MCP clients
- Uses **stdio** for communication (not suitable for notebooks)
- Best for: Interactive AI assistance, local development, testing

### 2. **Direct SDK Usage (Databricks Notebooks)**
- Runs **inside Databricks notebooks**
- Uses the **SAP BDC SDK directly** (no MCP layer needed)
- Has access to `dbutils` natively
- Best for: Scheduled jobs, production workflows, data pipelines

---

## Deployment Pattern 1: Local MCP Server (Current Setup)

**Where it runs**: Your local machine
**How it connects**: Environment variables + LocalDatabricksClient
**Use case**: Claude Desktop integration, local development

```bash
# On your local machine
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
export DATABRICKS_RECIPIENT_NAME="bdc-connect-12345"

# Run MCP server
python -m sap_bdc_mcp.server
```

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "sap-bdc": {
      "command": "python",
      "args": ["-m", "sap_bdc_mcp.server"],
      "env": {
        "DATABRICKS_RECIPIENT_NAME": "bdc-connect-12345"
      }
    }
  }
}
```

---

## Deployment Pattern 2: Databricks Notebook (Recommended for Databricks)

**Where it runs**: Inside Databricks notebooks
**How it connects**: Uses `dbutils` directly
**Use case**: Scheduled jobs, workflows, production pipelines

### Setup: Install the Package

```python
# In a Databricks notebook cell
%pip install sap-bdc-mcp-server
```

### Usage: Direct Function Calls (Not MCP)

Instead of using MCP tools, call the functionality directly:

#### Example 1: Provision a Share
```python
# Databricks Notebook - Provision Share Workflow
from databricks.sdk import WorkspaceClient
from bdc_connect_sdk.auth import DatabricksClient, BdcConnectClient

# Initialize clients (uses dbutils automatically in notebook)
databricks_client = DatabricksClient(
    dbutils=dbutils,
    recipient_name="bdc-connect-12345"
)
bdc_client = BdcConnectClient(databricks_client)
w = WorkspaceClient()

# Define share configuration
share_name = "production_customer_data"
tables = ["main.prod.customers", "main.prod.orders"]
recipient_name = "bdc-connect-12345"

# Step 1: Create Databricks share
try:
    w.shares.create(name=share_name, comment="Production customer data")
    print(f"✅ Created share: {share_name}")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"ℹ️ Share {share_name} already exists")
    else:
        raise

# Step 2: Add tables
for table in tables:
    try:
        w.shares.update(name=share_name, updates=[{
            "action": "ADD",
            "data_object": {"name": table, "data_object_type": "TABLE"}
        }])
        print(f"✅ Added table: {table}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"ℹ️ Table {table} already in share")
        else:
            raise

# Step 3: Grant to recipient
grant_sql = f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"
spark.sql(grant_sql)
print(f"✅ Granted to recipient: {recipient_name}")

# Step 4: Register with SAP BDC
ord_metadata = {
    "title": "Production Customer Data",
    "shortDescription": "Customer and order data for production analytics",
    "description": "Comprehensive customer dataset for business intelligence",
    "version": "1.0.0",
    "releaseStatus": "active",
    "tags": ["production", "customer", "analytics"]
}

result = bdc_client.create_or_update_share(
    share_name=share_name,
    body={"ord": ord_metadata, "objects": []}
)
print(f"✅ Registered with SAP BDC: {result.oid}")
```

#### Example 2: Validate Share Readiness
```python
# Databricks Notebook - Validate Share Function
def validate_share_readiness(share_name: str, recipient_name: str):
    """Validate that a share is ready for BDC registration."""

    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()
    checks = {}
    ready = True
    errors = []

    # Check 1: Share exists
    try:
        share_info = w.shares.get(share_name)
        checks["share_exists"] = "✅ PASS"
        print(f"✅ Share '{share_name}' exists")
    except Exception as e:
        checks["share_exists"] = "❌ FAIL"
        ready = False
        errors.append(f"Share '{share_name}' does not exist")
        print(f"❌ Share does not exist")
        return {"ready": False, "errors": errors, "checks": checks}

    # Check 2: Has objects
    try:
        share_details = w.shares.get(share_name)
        objects = share_details.objects if hasattr(share_details, 'objects') else []

        if objects and len(objects) > 0:
            checks["has_objects"] = f"✅ PASS ({len(objects)} objects)"
            print(f"✅ Share has {len(objects)} objects")
        else:
            checks["has_objects"] = "❌ FAIL"
            ready = False
            errors.append("Share has no tables")
            print(f"❌ Share has no objects")
    except Exception as e:
        checks["has_objects"] = f"⚠️ WARNING: {e}"
        print(f"⚠️ Could not check objects: {e}")

    # Check 3: Granted to recipient
    try:
        grants_sql = f"SHOW GRANTS ON SHARE {share_name}"
        grants_df = spark.sql(grants_sql)

        granted = False
        for row in grants_df.collect():
            if recipient_name in str(row):
                granted = True
                break

        if granted:
            checks["granted_to_recipient"] = "✅ PASS"
            print(f"✅ Granted to recipient: {recipient_name}")
        else:
            checks["granted_to_recipient"] = "❌ FAIL"
            ready = False
            errors.append(f"Not granted to recipient '{recipient_name}'")
            print(f"❌ NOT granted to recipient")
    except Exception as e:
        checks["granted_to_recipient"] = f"⚠️ WARNING: {e}"
        print(f"⚠️ Could not check grants: {e}")

    return {
        "ready": ready,
        "checks": checks,
        "errors": errors
    }

# Use it
validation = validate_share_readiness("production_customer_data", "bdc-connect-12345")

if validation["ready"]:
    print("\n✅ Share is ready for BDC registration!")
else:
    print(f"\n❌ Share is NOT ready. Errors:")
    for error in validation["errors"]:
        print(f"  - {error}")
```

#### Example 3: Scheduled Workflow
```python
# Databricks Notebook - Scheduled Data Product Deployment
from datetime import datetime

def deploy_data_product(share_name: str, tables: list, ord_metadata: dict):
    """Deploy a data product with full orchestration."""

    print(f"{'='*70}")
    print(f"Deploying Data Product: {share_name}")
    print(f"Time: {datetime.now()}")
    print(f"{'='*70}\n")

    from databricks.sdk import WorkspaceClient
    from bdc_connect_sdk.auth import DatabricksClient, BdcConnectClient

    # Initialize
    databricks_client = DatabricksClient(dbutils=dbutils, recipient_name=dbutils.widgets.get("recipient_name"))
    bdc_client = BdcConnectClient(databricks_client)
    w = WorkspaceClient()

    steps_completed = []

    try:
        # Validate first
        print("Step 0: Validating share...")
        validation = validate_share_readiness(share_name, databricks_client.recipient_name)

        if not validation["ready"]:
            # Create and setup
            print("Share not ready, provisioning...")

            # Create share
            w.shares.create(name=share_name)
            steps_completed.append("Created share")

            # Add tables
            for table in tables:
                w.shares.update(name=share_name, updates=[{
                    "action": "ADD",
                    "data_object": {"name": table, "data_object_type": "TABLE"}
                }])
                steps_completed.append(f"Added table: {table}")

            # Grant to recipient
            spark.sql(f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{databricks_client.recipient_name}`")
            steps_completed.append("Granted to recipient")
        else:
            print("✅ Share already ready, skipping provisioning")

        # Register with BDC
        print("Step 4: Registering with SAP BDC...")
        result = bdc_client.create_or_update_share(
            share_name=share_name,
            body={"ord": ord_metadata, "objects": []}
        )
        steps_completed.append("Registered with SAP BDC")

        print(f"\n{'='*70}")
        print("✅ DEPLOYMENT SUCCESSFUL")
        print(f"{'='*70}")
        print(f"Share OID: {result.oid}")
        print(f"Steps completed: {len(steps_completed)}")
        for step in steps_completed:
            print(f"  ✅ {step}")

        return result

    except Exception as e:
        print(f"\n{'='*70}")
        print("❌ DEPLOYMENT FAILED")
        print(f"{'='*70}")
        print(f"Error: {e}")
        print(f"\nSteps completed before failure:")
        for step in steps_completed:
            print(f"  ✅ {step}")
        raise

# Configure via widgets
dbutils.widgets.text("share_name", "")
dbutils.widgets.text("recipient_name", "bdc-connect-12345")

# Deploy
deploy_data_product(
    share_name=dbutils.widgets.get("share_name"),
    tables=["main.prod.customers", "main.prod.orders"],
    ord_metadata={
        "title": "Production Data Product",
        "version": "1.0.0",
        "releaseStatus": "active"
    }
)
```

---

## Deployment Pattern 3: Databricks Jobs (Production)

For production deployments, create a Databricks Job:

### Create Job via UI:
1. Go to **Workflows** → **Jobs**
2. Click **Create Job**
3. Configure:
   - **Task**: Python script or notebook
   - **Cluster**: Select or create cluster
   - **Schedule**: Cron expression for recurring runs
   - **Parameters**: Pass share names, recipient, etc.

### Example Job Configuration (JSON):
```json
{
  "name": "Deploy BDC Data Products",
  "tasks": [
    {
      "task_key": "deploy_customer_share",
      "notebook_task": {
        "notebook_path": "/Workspace/Production/deploy_bdc_share",
        "base_parameters": {
          "share_name": "prod_customer_data",
          "recipient_name": "bdc-connect-12345"
        }
      },
      "existing_cluster_id": "your-cluster-id"
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/Los_Angeles",
    "pause_status": "UNPAUSED"
  }
}
```

---

## Deployment Pattern 4: Databricks Apps (MCP over HTTP)

Databricks Apps can host MCP servers using **SSE (Server-Sent Events)** transport instead of stdio.

**Status**: ✅ **Supported** via MCP SSE transport

### Architecture

Instead of stdio (which won't work in Databricks Apps), use HTTP/SSE:

```
┌─────────────────────┐
│   AI Client         │
│   (Claude Desktop)  │
└──────────┬──────────┘
           │ HTTP/SSE
┌──────────▼──────────┐
│  Databricks App     │
│  ┌──────────────┐   │
│  │ FastAPI      │   │
│  │ + MCP SSE    │   │
│  └──────┬───────┘   │
│         │           │
│  ┌──────▼───────┐   │
│  │ SAP BDC      │   │
│  │ Tools        │   │
│  └──────────────┘   │
└─────────────────────┘
```

### Complete Implementation

#### 1. Project Structure
```
sap-bdc-mcp-app/
├── app.yaml                  # Databricks App configuration
├── app.py                    # FastAPI + MCP SSE server
├── requirements.txt          # Dependencies
├── src/
│   ├── __init__.py
│   ├── tools/
│   │   ├── share_tools.py   # Share management
│   │   └── validation.py    # Validation tools
│   └── config.py            # Configuration
└── .env.example
```

#### 2. Databricks App Configuration (app.yaml)
```yaml
command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

env:
  - name: DATABRICKS_HOST
    value: "{{workspace.host}}"
  - name: DATABRICKS_TOKEN
    value: "{{secrets.sap_bdc.databricks_token}}"
  - name: DATABRICKS_RECIPIENT_NAME
    value: "{{secrets.sap_bdc.recipient_name}}"
  - name: DATABRICKS_WAREHOUSE_ID
    value: "{{secrets.sap_bdc.warehouse_id}}"
```

#### 3. FastAPI + MCP SSE Server (app.py)
```python
"""SAP BDC MCP Server - Databricks App with SSE transport."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

# Import your existing BDC client manager
from src.sap_bdc_mcp.server import client_manager

app = FastAPI(title="SAP BDC MCP Server")

# Create MCP server instance
mcp = Server("sap-bdc-mcp-server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup."""
    # Initialize BDC clients
    client_manager.initialize()
    yield

app = FastAPI(lifespan=lifespan)

# Register tools
@mcp.list_tools()
async def list_tools():
    return [
        Tool(
            name="provision_share",
            description="End-to-end share provisioning",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {"type": "string"},
                    "tables": {"type": "array", "items": {"type": "string"}},
                    "ord_metadata": {"type": "object"}
                },
                "required": ["share_name", "tables", "ord_metadata"]
            }
        ),
        Tool(
            name="validate_share_readiness",
            description="Validate share readiness for BDC",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_name": {"type": "string"}
                },
                "required": ["share_name"]
            }
        ),
        # ... other tools
    ]

@mcp.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute tools - import from your existing implementation."""
    from src.sap_bdc_mcp.server import call_tool as execute_tool
    return await execute_tool(name, arguments)

# SSE endpoint for MCP
@app.get("/sse")
async def sse_endpoint():
    """Server-Sent Events endpoint for MCP."""
    async def event_generator():
        transport = SseServerTransport("/messages")

        async with mcp.run(
            transport.read_stream,
            transport.write_stream,
            mcp.create_initialization_options()
        ):
            # Keep connection alive
            while True:
                await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.post("/messages")
async def messages_endpoint(request: dict):
    """Handle MCP messages."""
    # Process MCP requests
    pass

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "sap-bdc-mcp-server"}
```

#### 4. Dependencies (requirements.txt)
```
fastapi>=0.104.0
uvicorn>=0.24.0
mcp>=1.0.0
sse-starlette>=1.6.5
sap-bdc-connect-sdk>=1.1.0
databricks-sdk>=0.18.0
python-dotenv>=1.0.0
```

#### 5. Deploy to Databricks Apps

**Prerequisites:**
```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token
```

**Create Secret Scope:**
```bash
# Create secret scope
databricks secrets create-scope sap_bdc

# Add secrets
databricks secrets put-secret sap_bdc databricks_token
databricks secrets put-secret sap_bdc recipient_name
databricks secrets put-secret sap_bdc warehouse_id
```

**Deploy App:**
```bash
# From project root
databricks apps create sap-bdc-mcp-server

# Deploy
databricks apps deploy sap-bdc-mcp-server \
  --source-code-path .

# Check status
databricks apps get sap-bdc-mcp-server
```

#### 6. Connect from Claude Desktop

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sap-bdc-databricks": {
      "url": "https://your-workspace.cloud.databricks.com/serving-endpoints/sap-bdc-mcp-server/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_DATABRICKS_TOKEN"
      }
    }
  }
}
```

### Key Differences: Databricks App vs Local

| Aspect | Local MCP Server | Databricks App MCP |
|--------|-----------------|-------------------|
| **Transport** | stdio | HTTP/SSE |
| **Hosting** | Your machine | Databricks managed |
| **Authentication** | .env file | Databricks secrets |
| **Scaling** | Single instance | Auto-scaling |
| **Availability** | When you run it | 24/7 |
| **Access** | Local only | Team-wide via URL |
| **Cost** | Free | Databricks compute |

### When to Use Databricks Apps

✅ **Use Databricks Apps when:**
- Multiple team members need access
- Want 24/7 availability
- Need centralized management
- Want to leverage Databricks secrets/security
- Team is already using Databricks

❌ **Use Local MCP Server when:**
- Personal development/testing
- Don't want to pay for Databricks compute
- Need quick iteration cycles
- Working offline

### Important Notes

1. **SSE vs stdio**: Databricks Apps require HTTP/SSE transport. The local MCP server uses stdio.

2. **Code Reuse**: The core tool logic (from `server.py`) can be reused. Only the transport layer changes.

3. **Secrets Management**: Use Databricks secrets instead of `.env` files for production.

4. **Monitoring**: Databricks Apps provide built-in logging and monitoring.

5. **Cost**: Running 24/7 will incur Databricks compute costs.

### Alternative: Serverless Deployment

For even lower cost, consider deploying as a **Databricks SQL Warehouse endpoint** or **AWS Lambda** with HTTP/SSE, but that requires more custom infrastructure.

**Recommendation**:
- **Development**: Local stdio MCP server
- **Production/Team**: Databricks App with SSE
- **Cost-sensitive**: Direct SDK usage in notebooks/jobs

---

## Comparison Table

| Aspect | Local MCP Server | Databricks Notebook | Databricks Job |
|--------|-----------------|-------------------|----------------|
| **Runs Where** | Your machine | Notebook session | Scheduled task |
| **Authentication** | Environment vars | dbutils | dbutils |
| **Best For** | Interactive AI | Ad-hoc tasks | Production automation |
| **MCP Protocol** | ✅ Yes | ❌ No (direct calls) | ❌ No (direct calls) |
| **Claude Integration** | ✅ Yes | ❌ No | ❌ No |
| **Scheduled Execution** | ❌ No | ⚠️ Manual | ✅ Yes |
| **Production Ready** | ❌ Dev only | ⚠️ With caution | ✅ Yes |

---

## Recommendation Summary

### For Interactive Development with Claude:
✅ **Use Local MCP Server** with LocalDatabricksClient

### For Databricks-Native Workflows:
✅ **Use Direct SDK Calls** in notebooks/jobs (no MCP layer)

### For Production Automation:
✅ **Use Databricks Jobs** with scheduled notebook execution

---

## Code Organization

```
Project Structure for Hybrid Usage:

sap-bdc-mcp-server/
├── src/sap_bdc_mcp/
│   ├── server.py              # MCP server (local use)
│   ├── local_client.py        # LocalDatabricksClient (local use)
│   └── databricks/            # NEW: Databricks-specific utilities
│       ├── __init__.py
│       ├── provision.py       # Provision share function
│       ├── validate.py        # Validate share function
│       └── workflows.py       # Common workflow patterns
├── notebooks/                  # NEW: Databricks notebooks
│   ├── Deploy_Data_Product.py
│   ├── Validate_Share.py
│   └── Scheduled_Sync.py
└── jobs/                       # NEW: Job definitions
    └── production_deployment.json
```

---

## Example: Reusable Databricks Module

Create `src/sap_bdc_mcp/databricks/provision.py`:

```python
"""Databricks-native share provisioning (no MCP)."""

from databricks.sdk import WorkspaceClient
from bdc_connect_sdk.auth import DatabricksClient, BdcConnectClient


def provision_share(
    share_name: str,
    tables: list[str],
    ord_metadata: dict,
    recipient_name: str,
    dbutils=None
):
    """Provision a share end-to-end in Databricks.

    Args:
        share_name: Name of the share
        tables: List of tables (catalog.schema.table format)
        ord_metadata: ORD metadata dict
        recipient_name: BDC recipient name
        dbutils: Databricks utilities (auto-detected if None)

    Returns:
        dict: Result with OID and status
    """
    # Auto-detect dbutils if not provided
    if dbutils is None:
        import IPython
        dbutils = IPython.get_ipython().user_ns.get('dbutils')

    # Initialize clients
    databricks_client = DatabricksClient(dbutils=dbutils, recipient_name=recipient_name)
    bdc_client = BdcConnectClient(databricks_client)
    w = WorkspaceClient()

    steps = []

    # Create share
    try:
        w.shares.create(name=share_name)
        steps.append(f"Created share: {share_name}")
    except Exception as e:
        if "already exists" not in str(e).lower():
            raise
        steps.append(f"Share exists: {share_name}")

    # Add tables
    for table in tables:
        w.shares.update(name=share_name, updates=[{
            "action": "ADD",
            "data_object": {"name": table, "data_object_type": "TABLE"}
        }])
        steps.append(f"Added table: {table}")

    # Grant to recipient
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()
    spark.sql(f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`")
    steps.append(f"Granted to: {recipient_name}")

    # Register with BDC
    result = bdc_client.create_or_update_share(
        share_name=share_name,
        body={"ord": ord_metadata, "objects": []}
    )
    steps.append(f"Registered with BDC: {result.oid}")

    return {
        "success": True,
        "oid": result.oid,
        "steps": steps
    }
```

**Use in notebook:**
```python
from sap_bdc_mcp.databricks.provision import provision_share

result = provision_share(
    share_name="customer_data",
    tables=["main.prod.customers"],
    ord_metadata={"title": "Customer Data", "version": "1.0.0"},
    recipient_name="bdc-connect-12345"
)

print(f"✅ Provisioned: {result['oid']}")
```

---

## Summary

**The MCP Server is for local/Claude Desktop use only.**

**For Databricks:**
- Extract the core logic from MCP tools
- Create Python functions that work natively in notebooks
- Use Databricks Jobs for scheduling
- Keep it simple - no stdio, no MCP protocol overhead

Would you like me to create the Databricks-native utility modules?
