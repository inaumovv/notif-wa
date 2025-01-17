from datetime import datetime

import requests
from requests import Response


class APIClient:

    def __init__(
            self,
            username: str,
            password: str,
            base_url: str,
            access_token: str | None = None,
            refresh_token: str | None = None,
    ):
        self.access_token: str | None = access_token
        self.refresh_token: str | None = refresh_token
        self.username: str = username
        self.password: str = password
        self.base_url: str = base_url

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token: str):
        self._access_token = access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token: str):
        self._refresh_token = refresh_token

    def login(self):
        data: dict[str, str] = {
            "username": self.username,
            "password": self.password
        }
        response: Response = requests.post(
            url=f'{self.base_url}auth/login/',
            data=data,
        )
        tokens: dict[str, str] = response.json()
        self.access_token = tokens["access"]
        self.refresh_token = tokens["refresh"]
        return tokens

    def get_rents(self, status: int, page_size: int):
        params: dict = {
            'status': status,
            'pageSize': page_size,
        }
        headers: dict[str, str] = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response: Response = requests.get(
            url=f'{self.base_url}crm/requests/',
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
