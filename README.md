# TUKOREA announce watcher

A minimal Python skeleton for a background announcement watcher application.

## Architecture

- **Watcher engine**: runs site adapters, compares current notices against stored state, and emits events for new notices.
- **Notifier**: abstract notification interface with a console implementation for local development.
- **Storage**: SQLite-backed store for previously seen notices and check history.
- **Scheduler**: APScheduler-based interval jobs so each site can be checked independently.
- **Adapters**: one module per site, with a shared interface that supports both lightweight HTTP scraping and heavier browser-backed workflows.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m announce_watcher.app
```

## Configuration model

Each site should define:

- `name`: stable site identifier.
- `interval_seconds`: polling interval.
- `enabled`: whether the site is active.
- `login_mode`: `none`, `session`, or `browser`.
- `settings`: site-specific configuration such as URLs or selectors.

See `announce_watcher/config.py` for the default in-code example.

## Extending with a real site

1. Create a new adapter in `announce_watcher/sites/`.
2. Implement `fetch_notices()` to return normalized `Notice` objects.
3. Register the adapter in `announce_watcher/config.py`.
4. Replace `ConsoleNotifier` with a Windows toast implementation when packaging for desktop use.
