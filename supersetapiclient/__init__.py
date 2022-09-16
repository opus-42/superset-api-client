# Configure logging
import logging

from supersetapiclient.client import SupersetClient  # noqa

FORMAT = "[%(asctime)-15s] %(levelname)s:%(name)s - %(message)s"

logging.basicConfig(format=FORMAT)
