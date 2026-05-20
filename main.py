"""Entry point — delegates to app.cli."""

import sys

from app.cli import _parse_args, _timestamp_folder_name, main  # noqa: F401 — re-exported for tests
from app.core.migration import run_first_time_migration
from app.core.user_data import ensure_user_data_dirs
from app.utils.logging_setup import setup_logging

if __name__ == "__main__":
    ensure_user_data_dirs()
    run_first_time_migration()
    _logger, _log_file = setup_logging()
    _logger.info("AI Adoption Metrics — starting CLI run")
    _logger.info("Log file: %s", _log_file)
    sys.exit(main())
