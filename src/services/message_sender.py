from whatsapp_api_client_python.API import GreenAPI


class MessageSender:

    def __init__(self, green_api: GreenAPI):
        self.green_api = green_api

    def send_message(self, number: str, message: str):
        # self.green_api.sending.sendMessage(f'{number}@c.us', message)
        self.green_api.sending.sendMessage(f'79268921668@c.us', message)
