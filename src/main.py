import logging

from whatsapp_api_client_python.API import GreenAPI

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

green_api: GreenAPI = GreenAPI(
    settings.ID_INSTANCE,
    settings.API_TOKEN_INSTANCE
)


