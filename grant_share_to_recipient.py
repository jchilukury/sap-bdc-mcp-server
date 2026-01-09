"""Grant a Databricks share to a recipient."""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Grant the test share to the BDC recipient."""

    print("=" * 60)
    print("Grant Databricks Share to Recipient")
    print("=" * 60)
    print()

    # Configuration
    share_name = "test_share_001"
    recipient_name = "bdc-connect-35c0d016"

    logger.info(f"Share: {share_name}")
    logger.info(f"Recipient: {recipient_name}")
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
        return

    # Grant the share to the recipient
    logger.info(f"Granting share '{share_name}' to recipient '{recipient_name}'...")
    print(f"This allows the recipient to access the share...")
    print()

    try:
        # Update the share to grant access to the recipient
        w.shares.update(
            name=share_name,
            updates=[
                {
                    "recipient": recipient_name,
                    "operation": "ADD"
                }
            ]
        )

        logger.info("SUCCESS: Share granted to recipient!")
        print()
        print("=" * 60)
        print("Share Successfully Granted!")
        print("=" * 60)
        print(f"Share: {share_name}")
        print(f"Recipient: {recipient_name}")
        print()
        print("=" * 60)
        print("Next Step:")
        print("=" * 60)
        print("Run: python test_create_share.py")
        print()
        print("This should now successfully register the share with SAP BDC!")
        print()

    except Exception as e:
        error_str = str(e)
        logger.error(f"Failed to grant share: {e}")
        print()
        print("Error details:")
        import traceback
        traceback.print_exc()
        print()

        if "updates" in error_str.lower() or "recipient" in error_str.lower():
            print("Alternative approach using SQL:")
            print(f"Run this in Databricks SQL Editor:")
            print()
            print(f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`;")
            print()
        else:
            print("Try granting the share manually:")
            print("  1. Go to Databricks workspace")
            print("  2. Navigate to Data > Delta Sharing")
            print(f"  3. Open share '{share_name}'")
            print("  4. Click 'Grant to Recipient'")
            print(f"  5. Select recipient '{recipient_name}'")

if __name__ == "__main__":
    main()
