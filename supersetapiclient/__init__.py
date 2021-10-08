from supersetapiclient.client import SupersetClient # noqa

# Configure logging
import logging

FORMAT = "[%(asctime)-15s] %(levelname)s:%(name)s - %(message)s"

logging.basicConfig(format=FORMAT)
