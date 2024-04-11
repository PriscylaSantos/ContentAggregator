import os
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo
import requests
import utils

from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()


class Globo(WebSite):

    __website_name: str = 'G1 Tecnologia'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'Globo({super().__repr__()})'

    @property
    def get_website_name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._Globo__website_name

    def execute(self, limit_pages: int = 10) -> None:

        page: int = 1
        name: str = 'arquivo_{num_page}.json'

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(page=str(page))
                status_code: int = response.status_code

                if status_code == 200:
                    data_globo: dict = response.json()
                    items_globo: list = data_globo.get('items', [])

                    items: list = self._generate_information(items_globo)
                    filename: str = name.format(num_page=page)
                    utils.save_json_file(self._base_path, filename, items)

                    page = data_globo.get('nextPage', page + 1)

                else:
                    _LOGGER.error(
                        f'Error fetching data from page {page}. URL: {response.url}, status_code: {status_code}'
                    )
                    page += 1

        except Exception as ex:
            _LOGGER.exception(ex)

        finally:
            _LOGGER.info('Finish \n')

    def _get_url(self, page: str) -> requests.models.Response:

        url: str = os.path.join(
            self._base_url, 'tenants/g1/instances/e361f955-0b39-4647-aecf-5ff3c6c137cc/posts/page', page
        )
        response: requests.models.Response = requests.get(
            url=url, cookies=self._cookies, headers=self._headers
        )
        return response

    def _generate_information(self, items: list) -> list:

        data: list = []
        for item in items:

            publication_date: Optional[str] = item.get('publication')
            if publication_date is not None:
                publication_date = self._convert_date(publication_date)

            update_date: Optional[str] = item.get('lastPublication')
            if update_date is not None:
                update_date = self._convert_date(update_date)

            content: dict = item.get('content', {})
            video: dict = content.get('video', {})
            if video is not None:
                video: str = video.get('url')

            image: Optional[str] = content.get('image', {}).get('sizes', {}).get('VM', {}).get('url')

            data.append({
                'website_name': self.get_website_name,
                'url': content.get('url'),
                'author': {
                    'name': None,
                    'url': None
                },
                'text': {
                    'title': content.get('title'),
                    'summary': content.get('summary'),
                    'publication_date': publication_date,
                    'update_date': update_date,
                    'image': image,
                    'audio': None,
                    'video': video,
                }
            })

        return data

    @staticmethod
    def _convert_date(date_str: str) -> str:
        try:
            date: datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            date: datetime = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')

        brasilia_datetime: datetime = date.replace(tzinfo=ZoneInfo('America/Sao_Paulo'))
        return brasilia_datetime.strftime("%Y-%m-%d %H:%M:%S")
