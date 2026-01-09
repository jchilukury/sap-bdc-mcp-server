"""Helper script to create a Delta Share in Databricks."""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Create a test Delta Share in Databricks."""

    print("=" * 60)
    print("Create Databricks Delta Share")
    print("=" * 60)
    print()

    # Initialize Databricks client
    logger.info("Initializing Databricks SDK...")
    try:
        from databricks.sdk import WorkspaceClient
        w = WorkspaceClient()
        logger.info("Databricks client initialized")
        print()
    except Exception as e:
        logger.error(f"Failed to initialize Databricks SDK: {e}")
        print("Make sure you have databricks-sdk installed and configured.")
        return

    # Define share name
    share_name = "test_share_001"

    logger.info(f"Creating share: {share_name}")
    print(f"Share name: {share_name}")
    print()

    try:
        # Create the share
        logger.info("Calling Databricks API to create share...")
        share = w.shares.create(
            name=share_name,
            comment="Test share for SAP BDC MCP Server integration"
        )

        logger.info(f"SUCCESS: Share created!")
        print()
        print("=" * 60)
        print("Share Created Successfully!")
        print("=" * 60)
        print(f"Name: {share.name}")
        if hasattr(share, 'comment'):
            print(f"Comment: {share.comment}")
        if hasattr(share, 'created_at'):
            print(f"Created at: {share.created_at}")
        print()

        # List all shares to verify
        logger.info("Listing all shares in workspace...")
        shares = list(w.shares.list())
        print(f"Total shares in workspace: {len(shares)}")
        for s in shares:
            print(f"  - {s.name}")
        print()

        print("=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print(f"1. Run: python test_create_share.py")
        print(f"   (Update share_name to '{share_name}')")
        print()
        print(f"2. Or use with Claude Desktop:")
        print(f"   'Register the share {share_name} with SAP BDC'")
        print()

    except Exception as e:
        error_str = str(e)

        if "ALREADY_EXISTS" in error_str or "already exists" in error_str.lower():
            logger.info(f"Share '{share_name}' already exists!")
            print()
            print("=" * 60)
            print("Share Already Exists")
            print("=" * 60)
            print(f"The share '{share_name}' already exists in your workspace.")
            print()
            print("You can:")
            print(f"  1. Use it: python test_create_share.py")
            print(f"  2. Delete it first: w.shares.delete('{share_name}')")
            print(f"  3. Choose a different name")
            print()

            # Try to list existing shares
            try:
                shares = list(w.shares.list())
                print(f"Existing shares ({len(shares)}):")
                for s in shares:
                    print(f"  - {s.name}")
            except:
                pass

        else:
            logger.error(f"Failed to create share: {e}")
            print()
            print("Error details:")
            import traceback
            traceback.print_exc()
            print()
            print("Common issues:")
            print("  - No permissions to create shares (need CREATE SHARE privilege)")
            print("  - Unity Catalog not fully configured")
            print("  - Network/authentication issues")
            print()
            print("Try creating the share manually:")
            print("  1. Go to Databricks workspace")
            print("  2. Navigate to Data > Delta Sharing")
            print("  3. Click 'Create Share'")

if __name__ == "__main__":
    main()
