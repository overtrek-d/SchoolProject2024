import yaml
import logging
from Crypto.Hash import SHA256

logger = logging.getLogger(__name__)

def config_load():
    try:
        with open("config.yaml") as f:
            return yaml.safe_load(f)
        logger.info("Loaded config")
    except Exception as e:
        logger.error(e)

def hash(value: str):
    return SHA256.new(value.encode('utf-8')).hexdigest()

