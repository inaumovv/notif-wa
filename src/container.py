from config import settings
from main import green_api
from services.api_client import APIClient
from services.case_manager import CaseManager
from services.message_sender import MessageSender
from services.message_text import MessageText
from services.payment_api_client import PaymentApiClient
from services.redis import Redis

redis: Redis = Redis(settings.REDIS_URL)

api_client: APIClient = APIClient(settings.API_USERNAME, settings.API_PASSWORD, settings.API_BASE_URL)
payment_api_client: PaymentApiClient = PaymentApiClient()

message_sender: MessageSender = MessageSender(green_api)
message_text: MessageText = MessageText()
case_manager: CaseManager = CaseManager(redis, message_sender, message_text, payment_api_client)

