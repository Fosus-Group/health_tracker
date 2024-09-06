import aiohttp
from aiohttp import (
    ClientConnectionError,
    ServerConnectionError,
    ServerDisconnectedError,
    ServerTimeoutError,
)
from core.config import Settings, get_app_settings
import json

app_settings: Settings = get_app_settings()


class SmsRuClient:
    """Клиент для работы с сервисом sms ru."""

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()

    async def make_phone_call(self, phone_number: str) -> str:
        params = {
            "phone": phone_number,
            "ip": "-1",
            "api_id": app_settings.smsru_api_id,
        }
        try:
            async with self._session.post(app_settings.smsru_api_url, params=params) as response:
                if response.status != 200:
                    raise Exception("Error while making phone call")
                response_text = await response.text()

                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    raise Exception(f"Failed to decode JSON: {response_text}")

                if response_data.get("status") == "OK":
                    last_4_digits = response_data.get("code")
                    return last_4_digits
                else:
                    raise Exception(f"Error in response: {response_data}")
        except (
                ClientConnectionError,
                ServerConnectionError,
                ServerDisconnectedError,
                ServerTimeoutError,
        ) as ex:
            raise Exception(f"Error while making phone call: {str(ex)}")
