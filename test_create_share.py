"""Test script to create a share in SAP BDC."""

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
    """Create a test share in SAP BDC."""

    print("=" * 60)
    print("SAP BDC - Create Test Share")
    print("=" * 60)
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

    # Get the BDC client
    logger.info("Step 2: Getting BDC Connect client...")
    try:
        bdc_client = client_manager.client
        logger.info(f"BDC client ready: {type(bdc_client).__name__}")
        print()
    except Exception as e:
        logger.error(f"Failed to get client: {e}")
        return

    # Use the existing Databricks share
    share_name = "test_share_001"  # Created in Databricks

    logger.info("Step 3: Creating test share...")
    print(f"Share name: {share_name}")
    print()

    # Define the request body
    # The body contains the ORD metadata and other share configuration
    request_body = {
        "ord": {
            "title": "Test Share",
            "shortDescription": "Test share created via MCP server",
            "description": "This is a test share to validate the SAP BDC MCP server integration",
            "version": "1.0.0",
            "releaseStatus": "active",
            "tags": ["test", "mcp", "validation"]
        },
        "objects": []  # Empty for now - just testing share creation
    }

    logger.info("Creating share with request body...")
    logger.info(f"Body: {json.dumps(request_body, indent=2)}")
    print()

    try:
        # Call the create_or_update_share method
        # Note: The actual SDK method signature is: create_or_update_share(share_name, body)
        result = bdc_client.create_or_update_share(
            share_name=share_name,
            body=request_body
        )

        logger.info("SUCCESS: Share registered with SAP BDC!")
        print()
        print("=" * 60)
        print("Result:")
        print("=" * 60)

        # Convert result to dict if it's an object
        if hasattr(result, '__dict__'):
            result_dict = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
            print(json.dumps(result_dict, indent=2, default=str))
        else:
            print(str(result))

        print()
        print("=" * 60)
        print(f"Share '{share_name}' registered with SAP BDC successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Failed to create share: {e}")
        print()
        print("Error details:")
        import traceback
        traceback.print_exc()
        print()
        print("This might be expected if:")
        print("  - You don't have permissions to create shares")
        print("  - The SAP BDC Connect endpoint is not configured")
        print("  - There are network connectivity issues")
        print()
        print("Check the error message above for specific details.")

if __name__ == "__main__":
    main()
