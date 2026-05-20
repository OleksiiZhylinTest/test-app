"""Entry point — delegates to app.server."""

from app.core.migration import run_first_time_migration
from app.core.user_data import ensure_user_data_dirs
from app.server import run
from app.utils.logging_setup import setup_logging

if __name__ == "__main__":
    ensure_user_data_dirs()
    run_first_time_migration()
    _logger, _log_file = setup_logging()
    _logger.info("AI Adoption Metrics — starting dev server")
    _logger.info("Log file: %s", _log_file)
    run()
