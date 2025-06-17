import logging
import sys
from pathlib import Path


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler('logs/parser.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout),
        ]
    )


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
