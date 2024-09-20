import uuid

import aiohttp
from aiohttp import (
    ClientConnectionError,
    ServerConnectionError,
    ServerDisconnectedError,
    ServerTimeoutError,
)
from core.config import Settings, get_app_settings
from datetime import datetime, timezone
from fastapi import UploadFile

import base64
import hmac
import hashlib
import mimetypes

app_settings: Settings = get_app_settings()


class YandexClient:
    """Клиент для работы с сервисами яндекса."""

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()

    async def upload_file(self, file: UploadFile) -> str:
        """Загрузка файла в yandex object storage."""

        mime_type = file.content_type or 'application/octet-stream'
        file_name = uuid.uuid4().hex

        resource = f"/{app_settings.bucket_name}/{file_name}"
        date_value = datetime.now(tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

        string_to_sign = f"PUT\n\n{mime_type}\n{date_value}\n{resource}"

        signature = base64.b64encode(
            hmac.new(app_settings.s3_secret.encode(), string_to_sign.encode(), hashlib.sha1).digest()
        ).decode()

        headers = {
            "Host": f"{app_settings.bucket_name}.storage.yandexcloud.net",
            "Date": date_value,
            "Content-Type": mime_type,
            "Authorization": f"AWS {app_settings.s3_key}:{signature}"
        }

        try:
            async with self._session.put(f"https://storage.yandexcloud.net/{app_settings.bucket_name}/{file_name}",
                                         headers=headers, data=file.file) as response:
                print(await response.text())
                if response.status != 200:
                    raise Exception(f"Failed to upload file: {response.status} - {await response.text()}")
                return file_name
        except (
                ClientConnectionError,
                ServerConnectionError,
                ServerDisconnectedError,
                ServerTimeoutError,
                FileNotFoundError,
        ) as ex:
            raise Exception(f"Error while uploading file: {str(ex)}")
