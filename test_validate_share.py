"""Test script for the validate_share_readiness tool."""

import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test the validate_share_readiness tool."""

    print("=" * 70)
    print("SAP BDC - Test Share Validation")
    print("=" * 70)
    print()

    # Initialize the client manager
    logger.info("Initializing BDC client manager...")
    try:
        from sap_bdc_mcp.server import client_manager
        client_manager.initialize()
        logger.info("Client manager initialized successfully")
        print()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        return

    # Test cases
    test_shares = [
        {
            "name": "test_share_001",
            "description": "Existing share that should be ready"
        },
        {
            "name": "nonexistent_share_xyz",
            "description": "Share that doesn't exist"
        }
    ]

    for test_case in test_shares:
        share_name = test_case["name"]
        description = test_case["description"]

        print("=" * 70)
        print(f"Test Case: {description}")
        print(f"Share: {share_name}")
        print("=" * 70)
        print()

        try:
            import os
            from databricks.sdk import WorkspaceClient

            w = client_manager.workspace_client
            recipient_name = client_manager.recipient_name

            validation_results = {
                "share_name": share_name,
                "ready_for_bdc": True,
                "checks": {},
                "warnings": [],
                "errors": [],
                "next_steps": []
            }

            # Check 1: Share exists
            logger.info(f"Checking if share '{share_name}' exists...")
            try:
                share_info = w.shares.get(share_name)
                validation_results["checks"]["share_exists"] = {
                    "status": "✅ PASS",
                    "message": f"Share '{share_name}' exists in Databricks"
                }
                print(f"  ✅ Share exists")
            except Exception as e:
                validation_results["ready_for_bdc"] = False
                validation_results["checks"]["share_exists"] = {
                    "status": "❌ FAIL",
                    "message": f"Share '{share_name}' does not exist",
                    "error": str(e)
                }
                validation_results["errors"].append(f"Share '{share_name}' not found")
                validation_results["next_steps"].append(f"Create share: w.shares.create(name='{share_name}')")
                print(f"  ❌ Share does not exist")

                # Can't check further if share doesn't exist
                print()
                print("Validation Summary:")
                print(f"  Status: ❌ NOT READY")
                print(f"  Reason: Share does not exist")
                print()
                continue

            # Check 2: Share has objects
            logger.info("Checking if share has objects...")
            try:
                share_details = w.shares.get(share_name)
                objects = share_details.objects if hasattr(share_details, 'objects') else []

                if objects and len(objects) > 0:
                    validation_results["checks"]["has_objects"] = {
                        "status": "✅ PASS",
                        "message": f"Share has {len(objects)} object(s)",
                        "objects": [obj.name for obj in objects]
                    }
                    print(f"  ✅ Share has {len(objects)} object(s)")
                    for obj in objects:
                        print(f"     - {obj.name}")
                else:
                    validation_results["ready_for_bdc"] = False
                    validation_results["checks"]["has_objects"] = {
                        "status": "❌ FAIL",
                        "message": "Share has no tables or objects"
                    }
                    validation_results["errors"].append("Share is empty")
                    validation_results["next_steps"].append("Add tables to the share")
                    print(f"  ❌ Share has no objects")
            except Exception as e:
                validation_results["warnings"].append(f"Could not check objects: {str(e)}")
                print(f"  ⚠️ Could not verify objects: {e}")

            # Check 3: Share granted to recipient
            logger.info("Checking if share is granted to recipient...")
            try:
                warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

                if warehouse_id:
                    grants_sql = f"SHOW GRANTS ON SHARE {share_name}"
                    grants_result = w.statement_execution.execute_statement(
                        warehouse_id=warehouse_id,
                        statement=grants_sql,
                        wait_timeout="30s"
                    )

                    granted_to_recipient = False
                    grants_list = []

                    if grants_result.result and grants_result.result.data_array:
                        for row in grants_result.result.data_array:
                            if row and len(row) > 0:
                                principal = str(row[0])
                                grants_list.append(principal)
                                if recipient_name in principal:
                                    granted_to_recipient = True

                    if granted_to_recipient:
                        validation_results["checks"]["granted_to_recipient"] = {
                            "status": "✅ PASS",
                            "message": f"Share is granted to recipient '{recipient_name}'"
                        }
                        print(f"  ✅ Granted to recipient: {recipient_name}")
                    else:
                        validation_results["ready_for_bdc"] = False
                        validation_results["checks"]["granted_to_recipient"] = {
                            "status": "❌ FAIL",
                            "message": f"Share is NOT granted to recipient '{recipient_name}'"
                        }
                        validation_results["errors"].append("Share not granted to recipient")
                        validation_results["next_steps"].append(
                            f"GRANT SELECT ON SHARE {share_name} TO RECIPIENT `{recipient_name}`"
                        )
                        print(f"  ❌ NOT granted to recipient: {recipient_name}")
                        if grants_list:
                            print(f"     Current grants: {', '.join(grants_list)}")
                else:
                    validation_results["warnings"].append("No warehouse configured")
                    print(f"  ⚠️ Cannot verify grants (DATABRICKS_WAREHOUSE_ID not set)")

            except Exception as e:
                validation_results["warnings"].append(f"Could not check grants: {str(e)}")
                print(f"  ⚠️ Could not check grants: {e}")

            # Summary
            print()
            print("-" * 70)
            if validation_results["ready_for_bdc"]:
                print("✅ VALIDATION PASSED - Share is ready for BDC Connect!")
                print()
                print("Next step:")
                print(f"  Register with: create_or_update_share('{share_name}', ...)")
            else:
                print("❌ VALIDATION FAILED - Share is NOT ready")
                print()
                if validation_results["errors"]:
                    print("Errors:")
                    for error in validation_results["errors"]:
                        print(f"  ❌ {error}")
                print()
                if validation_results["next_steps"]:
                    print("Required actions:")
                    for i, step in enumerate(validation_results["next_steps"], 1):
                        print(f"  {i}. {step}")

            if validation_results["warnings"]:
                print()
                print("Warnings:")
                for warning in validation_results["warnings"]:
                    print(f"  ⚠️ {warning}")

            print("-" * 70)
            print()

        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            print()
            print(f"❌ Error during validation: {e}")
            import traceback
            traceback.print_exc()
            print()

    print()
    print("=" * 70)
    print("Validation Testing Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
