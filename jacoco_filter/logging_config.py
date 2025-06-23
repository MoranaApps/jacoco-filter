import logging
import os
import sys


def setup_logging(is_verbose: bool = False) -> None:
    """
    Set up the logging configuration in the project

    @return: None
    """
    # Load logging configuration from the environment variables
    is_debug_mode = os.getenv("RUNNER_DEBUG", "0") == "1"
    level = logging.DEBUG if is_verbose or is_debug_mode else logging.INFO

    # Set up the logging configuration
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    sys.stdout.flush()

    logging.info("Logging configuration set up.")

    if is_verbose:
        logging.debug("Debug logging enabled.")
    if is_debug_mode:
        logging.debug("Debug mode enabled by CI runner.")