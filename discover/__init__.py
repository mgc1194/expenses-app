# discover/__init__.py

import logging
from .discover import process

# Setup logging
logging.basicConfig(level=logging.INFO)

logging.info("Initializing the discover package")
