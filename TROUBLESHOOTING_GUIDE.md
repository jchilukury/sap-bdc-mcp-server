# SAP BDC MCP Server - Troubleshooting Guide

## Common Issues and Solutions

Based on real-world usage and comprehensive testing.

---

## 1. Share Does Not Have ORD Annotations

### Error Message
```
Error: Share does not have ORD Annotations
```

### What This Means
The share exists in Databricks but hasn't been registered with SAP BDC Connect yet, or it was registered without ORD metadata.

### Solution Steps

**Step 1: Register the share with ORD metadata**
```python
# First, create/update the share with ORD metadata
result = bdc_client.create_or_update_share(
    share_name="your_share_name",
    body={
        "ord": {
            "title": "Your Share Title",
            "shortDescription": "Brief description",
            "description": "Detailed description of what this share contains",
            "version": "1.0.0",
            "releaseStatus": "active"
        }
    }
)
```

**Step 2: Now publish as data product**
```python
# After ORD metadata is set, you can publish
result = bdc_client.publish_data_product(
    share_name="your_share_name"
)
```

### Prevention
Always call `create_or_update_share` with ORD metadata before attempting to publish a data product.

---

## 2. Permission Denied / Share Not Granted to Recipient

### Error Message
```
Error: Share 'xxx' is not granted to recipient 'yyy'
PERMISSION_DENIED: Share not granted to recipient
```

### What This Means
The Databricks share exists but hasn't been granted to your BDC Connect recipient.

### Solution

**Using SQL (Recommended):**
```sql
-- In Databricks SQL Editor
GRANT SELECT ON SHARE your_share_name TO RECIPIENT `your_recipient_name`;

-- Verify the grant
SHOW GRANTS ON SHARE your_share_name;
```

**Using Python:**
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
w.statement_execution.execute_statement(
    warehouse_id="your_warehouse_id",
    statement=f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"
)
```

### Verification
```sql
-- Check what recipients have access
SHOW GRANTS ON SHARE your_share_name;

-- Should show: [recipient_name, SELECT]
```

---

## 3. Share Does Not Exist

### Error Message
```
NOT_FOUND: SHARE_DOES_NOT_EXIST: Share 'xxx' does not exist
```

### What This Means
The share hasn't been created in Databricks yet. Remember: **SAP BDC Connect works with existing Databricks shares**.

### Solution

**Step 1: Create the share in Databricks**

Using SQL:
```sql
CREATE SHARE IF NOT EXISTS your_share_name
COMMENT 'Description of your share';

-- Add tables to the share
ALTER SHARE your_share_name
ADD TABLE catalog_name.schema_name.table_name;

-- View the share
DESCRIBE SHARE your_share_name;
```

Using Python:
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
w.shares.create(
    name="your_share_name",
    comment="Description of your share"
)
```

**Step 2: Grant to recipient**
```sql
GRANT SELECT ON SHARE your_share_name TO RECIPIENT `your_recipient_name`;
```

**Step 3: Register with SAP BDC**
```python
result = bdc_client.create_or_update_share(
    share_name="your_share_name",
    body={
        "ord": {
            "title": "Your Share",
            "shortDescription": "Brief description",
            "version": "1.0.0"
        }
    }
)
```

---

## 4. CSN Schema Format Issues

### Error Message
```
Error: Invalid CSN schema format
Error: Table reference not found
```

### What This Means
The CSN (Common Semantic Notation) schema has incorrect table references or format.

### Correct CSN Format

**Important**: Use `schema.table` format (not just `table`):

```python
csn_schema = {
    "definitions": {
        "schema_name.table_name": {  # ✅ Correct: schema.table
            "kind": "entity",
            "elements": {
                "id": {"type": "cds.Integer"},
                "name": {"type": "cds.String"}
            }
        }
    }
}
```

**Incorrect formats:**
```python
# ❌ Wrong: Just table name
"table_name": {...}

# ❌ Wrong: Catalog.schema.table
"catalog.schema.table": {...}

# ✅ Right: schema.table
"schema.table": {...}
```

### Common CSN Data Types

```python
"elements": {
    "id": {"type": "cds.Integer"},           # Integer numbers
    "name": {"type": "cds.String"},          # Text strings
    "amount": {"type": "cds.Decimal"},       # Decimal numbers
    "created_at": {"type": "cds.Timestamp"}, # Timestamps
    "is_active": {"type": "cds.Boolean"}     # True/False
}
```

---

## 5. BDC Client Not Initialized

### Error Message
```
RuntimeError: BDC client not initialized. Call initialize() first.
```

### Solution for Local Development

**Check your .env file:**
```bash
# Required variables
DATABRICKS_RECIPIENT_NAME=your_recipient_name
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...

# Optional
LOG_LEVEL=INFO
```

**Verify environment loading:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print("Host:", os.getenv("DATABRICKS_HOST"))
print("Token:", "present" if os.getenv("DATABRICKS_TOKEN") else "missing")
print("Recipient:", os.getenv("DATABRICKS_RECIPIENT_NAME"))
```

### Solution for Notebook Environment

Set environment variable in your notebook:
```python
import os
os.environ["DATABRICKS_RECIPIENT_NAME"] = "your_recipient_name"
```

---

## 6. Invalid Databricks Token

### Error Message
```
Error 401: Unauthorized
Invalid authentication credentials
```

### Solution

**Generate a new token:**
1. Go to Databricks workspace
2. Click your profile → User Settings
3. Developer → Access Tokens
4. Generate new token
5. Copy and update in `.env` file

**Verify token:**
```python
import requests

response = requests.get(
    "https://your-workspace.cloud.databricks.com/api/2.0/clusters/list",
    headers={"Authorization": f"Bearer {your_token}"}
)
print(response.status_code)  # Should be 200
```

---

## 7. Workspace URL Issues

### Error Message
```
Error: Failed to connect to workspace
Connection timeout
```

### Common Issues

**❌ Wrong format:**
```
http://workspace.cloud.databricks.com  # Missing https
workspace.cloud.databricks.com         # Missing protocol
https://workspace.databricks.com/      # Trailing slash
```

**✅ Correct format:**
```
https://workspace.cloud.databricks.com
```

### Verification
```bash
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
     https://your-workspace.cloud.databricks.com/api/2.0/clusters/list
```

---

## 8. Network and Firewall Issues

### Error Message
```
Connection timeout
SSL certificate verification failed
```

### Solutions

**Check connectivity:**
```python
import requests

try:
    response = requests.get(
        "https://your-workspace.cloud.databricks.com",
        timeout=10
    )
    print("Connection OK")
except requests.exceptions.SSLError:
    print("SSL certificate issue")
except requests.exceptions.ConnectionError:
    print("Cannot reach workspace")
except requests.exceptions.Timeout:
    print("Connection timeout")
```

**For SSL issues (corporate proxy):**
```python
import os
os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/corporate/ca-bundle.crt'
```

---

## 9. Recipient Not Found

### Error Message
```
Error: Recipient 'xxx' not found
```

### Solution

**List all recipients:**
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
recipients = list(w.recipients.list())

print("Available recipients:")
for r in recipients:
    print(f"  - {r.name}")
```

**Verify recipient name:**
- Names are case-sensitive
- Check for extra spaces
- Verify the exact recipient ID from Databricks UI

---

## 10. SQL Warehouse Issues

### Error Message
```
Error: Warehouse not available
RESOURCE_DOES_NOT_EXIST: Warehouse does not exist
```

### Solution

**Check warehouse status:**
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
warehouses = list(w.warehouses.list())

for wh in warehouses:
    print(f"Name: {wh.name}")
    print(f"ID: {wh.id}")
    print(f"State: {wh.state}")
```

**Start a stopped warehouse:**
```python
w.warehouses.start(id="your_warehouse_id")
```

---

## Quick Reference: Complete Workflow

### 1. Create Share in Databricks
```sql
CREATE SHARE my_share;
ALTER SHARE my_share ADD TABLE catalog.schema.table;
```

### 2. Grant to Recipient
```sql
GRANT SELECT ON SHARE my_share TO RECIPIENT `my_recipient`;
```

### 3. Register with SAP BDC
```python
bdc_client.create_or_update_share(
    share_name="my_share",
    body={"ord": {"title": "My Share", "version": "1.0.0"}}
)
```

### 4. Publish as Data Product (Optional)
```python
bdc_client.publish_data_product(share_name="my_share")
```

---

## Getting Help

### Check Logs
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m sap_bdc_mcp.server
```

### Verify Configuration
```bash
python -c "
from sap_bdc_mcp.local_client import LocalDatabricksClient
client = LocalDatabricksClient.from_env()
print(f'Workspace: {client.databricks_workspace_url}')
print(f'Recipient: {client.recipient_name}')
print(f'Mode: BDC Connect' if client.is_brownfield_environment else 'Databricks Connect')
"
```

### Test Connection
```bash
python test_create_share.py
```

---

## Additional Resources

- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[HOW_TO_CREATE_SHARE.md](HOW_TO_CREATE_SHARE.md)** - Complete workflow
- **[IMPLEMENTATION_SUCCESS.md](IMPLEMENTATION_SUCCESS.md)** - Technical details
- **[GitHub Issues](https://github.com/MarioDeFelipe/sap-bdc-mcp-server/issues)** - Report problems

---

**Remember**: Most issues are related to permissions or the workflow sequence. Always:
1. ✅ Create share in Databricks first
2. ✅ Grant to recipient
3. ✅ Register with SAP BDC
4. ✅ Then publish (if needed)
