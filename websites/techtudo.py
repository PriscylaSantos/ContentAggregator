import os
from typing import Optional
import requests
import utils

from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()


class TechTudo(WebSite):
    __website_name: str = 'TechTudo'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'TechTudo({super().__repr__()})'

    @property
    def get_website_name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._TechTudo__website_name

    def execute(self, limit_pages: int = 10) -> None:
        page: int = 1
        name: str = 'arquivo_{num_page}.json'

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(page=str(page))
                status_code: int = response.status_code

                if status_code == 200:

                    data_techtudo: dict = response.json()
                    items_techtudo: list = data_techtudo.get('items', [])

                    items: list = self._generate_information(items_techtudo)
                    filename = name.format(num_page=page)
                    utils.save_json_file(self._base_path, filename, items)

                    page = data_techtudo.get('nextPage', page + 1)

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
            self._base_url, 'tenants/techtudo/instances/965d44ab-5f2d-4552-b136-d609c7bef221/posts/page', page
        )
        response: requests.models.Response = requests.get(
            url=url, headers=self._headers
        )
        return response

    def _generate_information(self, items: list) -> list:

        data: list = []
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        for item in items:

            publication_date: Optional[str] = item.get('publication')
            if publication_date is not None:
                publication_date = utils.convert_date(publication_date, date_format)

            update_date: Optional[str] = item.get('lastPublication')
            if update_date is not None:
                update_date = utils.convert_date(update_date, date_format)

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
