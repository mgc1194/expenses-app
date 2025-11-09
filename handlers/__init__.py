# handlers/__init__.py
import logging
from .capital_one_handler import process
from .sofi_handler import process
from .amex_handler import process
from .chase_handler import process
from .wells_fargo_handler import process
from .discover_handler import process

# Setup logging
logging.basicConfig(level=logging.INFO)

logging.info("Initializing the handlers package")
