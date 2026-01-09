"""Grant a Databricks share to a recipient using SQL."""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Grant the test share to the BDC recipient using SQL."""

    print("=" * 60)
    print("Grant Share to Recipient (via SQL)")
    print("=" * 60)
    print()

    # Configuration
    share_name = "test_share_001"
    recipient_name = "bdc-connect-35c0d016"
    warehouse_id = "23c6f27c2bb68071"  # From .env

    logger.info(f"Share: {share_name}")
    logger.info(f"Recipient: {recipient_name}")
    logger.info(f"Using SQL Warehouse: {warehouse_id}")
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

    # Execute SQL to grant the share
    sql_grant = f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"

    logger.info("Executing SQL command...")
    logger.info(f"SQL: {sql_grant}")
    print()

    try:
        # Execute the SQL statement
        result = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=sql_grant,
            wait_timeout="30s"
        )

        logger.info("SUCCESS: Share granted to recipient!")
        print()
        print("=" * 60)
        print("Share Successfully Granted!")
        print("=" * 60)
        print(f"Share: {share_name}")
        print(f"Recipient: {recipient_name}")
        print()

        # Verify by showing grants
        logger.info("Verifying grants...")
        verify_sql = f"SHOW GRANTS ON SHARE {share_name}"
        verify_result = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=verify_sql,
            wait_timeout="30s"
        )

        if verify_result.result and verify_result.result.data_array:
            print("Current grants on share:")
            for row in verify_result.result.data_array:
                print(f"  {row}")
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
        print("Manual approach:")
        print("  1. Go to Databricks workspace SQL Editor")
        print("  2. Run this SQL command:")
        print()
        print(f"     {sql_grant}")
        print()
        print("Or use the UI:")
        print("  1. Navigate to Data > Delta Sharing")
        print(f"  2. Open share '{share_name}'")
        print("  3. Click 'Grant to Recipient'")
        print(f"  4. Select '{recipient_name}'")

if __name__ == "__main__":
    main()
