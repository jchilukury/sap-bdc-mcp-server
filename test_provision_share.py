"""Test script to provision a complete share using the orchestration tool."""

import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test the provision_share orchestration tool."""

    print("=" * 70)
    print("SAP BDC - Test Share Provisioning (End-to-End)")
    print("=" * 70)
    print()

    # Initialize the client manager
    logger.info("Step 1: Initializing BDC client manager...")
    try:
        from sap_bdc_mcp.server import client_manager
        client_manager.initialize()
        logger.info("Client manager initialized successfully")
        print()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        return

    # Example: Provision a new share end-to-end
    share_name = f"test_provisioned_share_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    logger.info("Test Configuration:")
    print(f"Share name: {share_name}")
    print(f"Tables: main.default.iris_data")
    print()

    # This simulates what the provision_share MCP tool does
    logger.info("Starting end-to-end provisioning workflow...")
    print()

    try:
        from databricks.sdk import WorkspaceClient
        import os

        w = client_manager.workspace_client
        bdc_client = client_manager.client
        recipient_name = client_manager.recipient_name

        steps_completed = []

        # Step 1: Create Databricks share
        logger.info("Step 1/4: Creating Databricks share...")
        try:
            w.shares.create(
                name=share_name,
                comment="Test share created via provision_share tool"
            )
            steps_completed.append(f"✅ Created Databricks share '{share_name}'")
            print("  ✅ Share created")
        except Exception as e:
            if "already exists" in str(e).lower():
                steps_completed.append(f"ℹ️ Share '{share_name}' already exists")
                print("  ℹ️ Share already exists, continuing...")
            else:
                raise

        # Step 2: Add tables to share
        logger.info("Step 2/4: Adding tables to share...")
        tables = ["main.default.iris_data"]
        for table in tables:
            try:
                w.shares.update(name=share_name, updates=[{
                    "action": "ADD",
                    "data_object": {"name": table, "data_object_type": "TABLE"}
                }])
                steps_completed.append(f"  ✅ Added table: {table}")
                print(f"  ✅ Added table: {table}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    steps_completed.append(f"  ℹ️ Table {table} already in share")
                    print(f"  ℹ️ Table {table} already in share")
                else:
                    raise

        # Step 3: Grant to recipient
        logger.info("Step 3/4: Granting share to recipient...")
        warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
        grant_sql = f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"

        try:
            w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=grant_sql,
                wait_timeout="30s"
            )
            steps_completed.append(f"✅ Granted to recipient '{recipient_name}'")
            print(f"  ✅ Granted to recipient: {recipient_name}")
        except Exception as e:
            if "already granted" in str(e).lower():
                steps_completed.append(f"ℹ️ Already granted to recipient")
                print("  ℹ️ Already granted to recipient")
            else:
                raise

        # Step 4: Register with SAP BDC
        logger.info("Step 4/4: Registering with SAP BDC...")
        ord_metadata = {
            "title": "Test Provisioned Share",
            "shortDescription": "Share created via provision_share tool",
            "description": "This share was created using the end-to-end provisioning workflow",
            "version": "1.0.0",
            "releaseStatus": "active",
            "tags": ["test", "provisioned", "automated"]
        }

        request_body = {
            "ord": ord_metadata,
            "objects": []
        }

        result = bdc_client.create_or_update_share(
            share_name=share_name,
            body=request_body
        )
        steps_completed.append(f"✅ Registered with SAP BDC")
        print("  ✅ Registered with SAP BDC")

        # Display results
        print()
        print("=" * 70)
        print("✅ PROVISIONING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Steps Completed:")
        for step in steps_completed:
            print(f"  {step}")
        print()
        print("SAP BDC Registration Result:")
        print("-" * 70)
        if hasattr(result, '__dict__'):
            result_dict = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
            print(json.dumps(result_dict, indent=2, default=str))
        else:
            print(str(result))
        print()
        print("=" * 70)
        print(f"Share '{share_name}' is now ready for use!")
        print("=" * 70)
        print()
        print("This demonstrates the complete workflow that the 'provision_share'")
        print("MCP tool automates in a single call.")

    except Exception as e:
        logger.error(f"Provisioning failed: {e}")
        print()
        print("=" * 70)
        print("❌ PROVISIONING FAILED")
        print("=" * 70)
        print()
        print("Error details:")
        import traceback
        traceback.print_exc()
        print()
        if steps_completed:
            print("Steps completed before failure:")
            for step in steps_completed:
                print(f"  {step}")

if __name__ == "__main__":
    main()
