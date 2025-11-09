# wells_fargo/__init__.py
import logging
from .savings import process
from .checking import process

# Setup logging
logging.basicConfig(level=logging.INFO)

logging.info("Initializing the wells_fargo package")
