# How to Create a Share in SAP BDC

## Understanding the Workflow

The SAP BDC Connect SDK works with **existing Databricks Delta Shares**. The workflow is:

1. **Create a Delta Share in Databricks** (using Databricks Unity Catalog)
2. **Register the share with SAP BDC** (using the MCP server/SDK)
3. **Publish as a data product** (optional)

You cannot create a share directly in BDC without first having it in Databricks.

## Current Status

**Checked your Databricks workspace**: No Delta Shares found yet.

## Step-by-Step Guide to Create Your First Share

### Option 1: Create Share via Databricks UI (Easiest)

1. **Go to your Databricks workspace**:
   - URL: https://dbc-a413df6c-f111.cloud.databricks.com

2. **Navigate to Data**:
   - Click "Data" in the left sidebar
   - Go to the "Delta Sharing" tab

3. **Create a new share**:
   - Click "Create Share"
   - Name it: `test_share_001`
   - Add a description

4. **Add tables to the share** (optional for testing):
   - You can add tables from your catalogs
   - Or leave it empty for now

5. **Save the share**

### Option 2: Create Share via SQL (Faster)

Open a SQL Editor in Databricks and run:

```sql
-- Create a share
CREATE SHARE IF NOT EXISTS test_share_001
COMMENT 'Test share for SAP BDC integration';

-- Optionally: Add a table to the share
-- ALTER SHARE test_share_001 ADD TABLE <catalog>.<schema>.<table_name>;

-- View the share
SHOW SHARES;

-- View details
DESCRIBE SHARE test_share_001;
```

### Option 3: Create Share via Databricks SDK (Programmatic)

Create a file `create_databricks_share.py`:

```python
from databricks.sdk import WorkspaceClient

# Initialize client (uses .env credentials)
w = WorkspaceClient()

# Create a share
share_name = "test_share_001"

try:
    # Create the share
    w.shares.create(
        name=share_name,
        comment="Test share for SAP BDC integration"
    )
    print(f"Share '{share_name}' created successfully!")

    # List all shares to verify
    shares = list(w.shares.list())
    print(f"\\nTotal shares: {len(shares)}")
    for share in shares:
        print(f"  - {share.name}")

except Exception as e:
    print(f"Error: {e}")
```

Run it:
```bash
python create_databricks_share.py
```

## After Creating the Databricks Share

Once you have a share in Databricks, you can use the MCP server to register it with SAP BDC:

### Update the Test Script

Edit `test_create_share.py` and change:

```python
share_name = f"test_share_{timestamp}"
```

To use your actual Databricks share name:

```python
share_name = "test_share_001"  # Use the name from Databricks
```

Then run:
```bash
python test_create_share.py
```

### Or Test via MCP Tool Directly

Once integrated with Claude Desktop, you can say:

```
"Register the Databricks share 'test_share_001' with SAP BDC"
```

## Understanding the Error You Saw

The error message was:
```
SHARE_DOES_NOT_EXIST: Share 'test_share_20260109_205908' does not exist
```

This means:
- The BDC SDK tried to get an access token for the share
- Databricks returned that the share doesn't exist
- **This is expected** - you need to create the share in Databricks first

## What the MCP Server Actually Does

When you call `create_or_update_share`:

1. **Gets access token** from Databricks for the share (requires share to exist)
2. **Registers the share** with SAP BDC Connect
3. **Updates ORD metadata** (title, description, etc.)
4. **Configures federation** between Databricks and SAP BDC

It does NOT create the underlying Databricks Delta Share.

## Quick Test Without Creating Actual Data

If you just want to test the MCP server functionality without setting up actual data:

1. Create an empty share in Databricks (Option 2 above - SQL method)
2. Register it with SAP BDC using the test script
3. The share will be registered even without any tables

## Next Steps

1. **Choose one of the options above** to create a Databricks share
2. **Update and run** `test_create_share.py` with the actual share name
3. **Verify registration** by checking SAP BDC portal (if you have access)
4. **Add tables** to the share later when you have actual data to share

## Need Help?

If you need help creating a share in Databricks:
- Check Databricks documentation: https://docs.databricks.com/data-sharing/
- Review Unity Catalog requirements
- Ensure you have the necessary permissions (CREATE SHARE privilege)

---

**Remember**: The MCP server is working correctly! It just needs an existing Databricks share to register with SAP BDC. 🎯
