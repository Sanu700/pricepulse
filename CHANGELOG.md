# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- BigBasket provider and normalized multi-provider result shape.
- Local store logos and local product placeholder asset.
- Targeted stale-search refresh task and provider concurrency controls.
- Test settings for SQLite-backed CI validation.
- Repository documentation (`docs/`) and GitHub project templates.

### Changed
- Product comparison rows now expose MRP, discount %, and delivery ETA.
- Product cards/details use self-hosted brand assets and safer fallbacks.
- Docker Compose backend now uses the image default Gunicorn command.
- Notification status endpoint is admin-only.
- Authenticated price alerts are tied to the signed-in account email.

### Fixed
- Frontend lint issues around effect-driven state sync.
- Suggestion dropdown stale-result race condition.
- Product stats endpoint extra per-store history queries.
- Missing price-history indexes for current query patterns.
- Footer localhost-only API docs link.