# Changelog

## [0.5.0] - 2026-05-02

### Added — driven by SAP help.sap.com 2026-05-02 batch (3 PDFs)
- **`validate_databricks_privileges`** — pre-flight check that the executing principal has the 6 metastore privileges required for BDC sharing: CREATE CATALOG, CREATE SHARE, SET SHARE PERMISSION, USE PROVIDER, USE RECIPIENT, USE SHARE. Source: SAP help.sap.com "Working with Data Products in SAP Databricks".
- **`validate_ord_metadata`** — local ORD JSON validation. Catches the most common publish failures before round-tripping the SDK. Rules: required `title`/`shortDescription`/`description`; `description` must NOT contain `shortDescription` (explicit SAP rule); `visibility` ∈ {public, interval, private}; `releaseStatus` ∈ {active, beta, deprecated}; ISO 8601 dates; sunsetDate ≥ deprecationDate.
- **`list_unsupported_share_assets`** — scan a Databricks catalog/schema and flag assets that cannot be shared via Delta Sharing to BDC. As of May 2026 the only known unsupported type is materialized views.

### Changed
- `create_or_update_share` now runs `validate_ord_metadata` automatically before forwarding to the SDK. Bypass with `skip_validation=true`.
- `sap-bdc-connect-sdk` dependency loosened from `>=1.1.6` to `>=1.0.9` to match the SAP-published reference version. By the way, the previous `==1.1.13` pin in the bundled plugin skill was incorrect; replaced with a `>=` floor.
- Description updated to reflect 17 tools (was 14).

### Notes
- **Deletion vectors clarification**: SAP Note 3706399 (delete vectors break inbound sharing) and the new derived-DP guide (enable delete vectors on your own derived tables) do NOT contradict — they cover opposite sides of the share.
- Bumped from 0.3.0 → 0.5.0 (skipping 0.4.0 — that version was a plugin-only release).


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- npm package for Node.js/TypeScript integration
- Docker images for containerized deployment
- Caching layer for improved performance
- Permission-based authorization system
- Data quality validation tools
- Batch operations support

## [0.2.0] - 2026-01-10

### Added

#### New MCP Tools ✨
- **`provision_share`** - End-to-end share provisioning orchestration
  - Creates Databricks share in one operation
  - Adds tables to the share automatically
  - Grants share to recipient with SQL execution
  - Registers with SAP BDC
  - Provides step-by-step progress feedback
  - Idempotent and fault-tolerant design
  - Handles partial failures gracefully

- **`validate_share_readiness`** - Pre-flight validation tool
  - Validates share exists in Databricks
  - Checks share has tables/objects
  - Verifies share is granted to recipient
  - Optionally checks BDC registration status
  - Returns structured validation results
  - Provides actionable next steps for failures
  - Prevents "trial and error" registration attempts

#### Major Documentation Additions
- **BLOG_POST_VALIDATION_TOOL.md** - Comprehensive blog post content
  - Use case-driven stories (before/after comparisons)
  - 5 detailed real-world use cases
  - Metrics: 70% faster onboarding, 80% fewer failed attempts, 83% fewer support tickets
  - Code examples and integration patterns
  - CI/CD pipeline examples

- **DATABRICKS_DEPLOYMENT.md** - Multi-pattern deployment guide
  - Pattern 1: Local MCP Server (stdio transport)
  - Pattern 2: Databricks Notebooks (direct SDK usage)
  - Pattern 3: Databricks Jobs (scheduled automation)
  - Pattern 4: Databricks Apps (SSE transport for team-wide 24/7 access)
  - Complete implementation examples for each pattern
  - Comparison tables and decision guidance

- **MCP_SERVER_COMPARISON.md** - Strategic analysis and roadmap
  - Comparison with SAP Datasphere MCP (7 tools vs 45 tools)
  - Expansion roadmap to v1.0.0 with 3 phases
  - Publishing strategy (PyPI, npm, Docker, documentation site)
  - Community building and content marketing plans
  - Metrics to track adoption and quality

- **TROUBLESHOOTING_GUIDE.md** - Common issues and solutions
  - 10 common error scenarios with detailed fixes
  - ORD annotation configuration issues
  - Permission and grant problems
  - Network and authentication troubleshooting
  - Workspace URL and token validation

#### Testing & Examples
- **test_validate_share.py** - Validation tool test script
  - Demonstrates validation workflow
  - Tests both existing and non-existent shares
  - Shows structured output format with pass/fail/warning states

### Improved

#### Core Functionality
- **BDCClientManager** enhancements
  - Added `workspace_client` property for Databricks SDK operations
  - Added `recipient_name` property for easier access
  - Better initialization error messages
  - Proper client lifecycle management

- **Error handling and user feedback**
  - Step-by-step progress reporting in `provision_share`
  - Clear error messages with recovery guidance at each step
  - Warnings vs errors distinction in validation
  - Actionable next steps for all failure modes

- **Documentation coverage**
  - README updated with all 7 tools documented
  - Each tool now has comprehensive parameter documentation
  - Use cases and workflow guidance added
  - Real-world examples for each tool

### Changed
- Updated README status from v0.1.0 to current development state
- Enhanced tool descriptions with more detail
- Improved code examples to show complete workflows

### Technical Improvements
- Enhanced type hints throughout codebase
- Better async/await patterns in MCP handlers
- Improved logging with structured messages
- More robust error recovery in orchestration flows
- Warehouse ID validation for SQL operations

### Developer Experience
- Examples now show complete workflows (validation → provision → verify)
- Better separation of concerns between validation and execution
- Self-service troubleshooting via validation tool
- CI/CD friendly validation patterns with exit codes
- Clear upgrade path from manual to automated workflows

### Performance
- Validation checks run in parallel where possible
- Reduced redundant API calls in provision flow
- Better error short-circuiting (fail fast)

## [0.1.0] - 2025-12-16

### Added
- Initial release of SAP BDC MCP Server
- Support for 5 core SAP BDC operations:
  - `create_or_update_share` - Create/update data shares with ORD metadata
  - `create_or_update_share_csn` - Configure shares using CSN schema
  - `publish_data_product` - Publish data products
  - `delete_share` - Delete and withdraw shares
  - `generate_csn_template` - Auto-generate CSN templates
- MCP protocol implementation using stdio transport
- Configuration management via environment variables
- Databricks integration support
- Delta Sharing protocol support
- Comprehensive test suite
- Documentation and examples
- GitHub Actions CI/CD workflows
- MIT License

### Technical Details
- Python 3.9+ support
- Compatible with SAP BDC Connect SDK 1.1.6+
- MCP SDK integration
- Type hints throughout codebase
- Async/await support for MCP operations

### Known Limitations
- Requires Databricks environment with dbutils
- Recipient configuration needed for Delta Sharing
- Limited to SAP BDC Connect SDK exposed functionality

---

## Release Notes Template

### [Version] - YYYY-MM-DD

#### Added
- New features

#### Changed
- Changes in existing functionality

#### Deprecated
- Soon-to-be removed features

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Security improvements

---

[Unreleased]: https://github.com/MarioDeFelipe/sap-bdc-mcp-server/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/MarioDeFelipe/sap-bdc-mcp-server/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/MarioDeFelipe/sap-bdc-mcp-server/releases/tag/v0.1.0
