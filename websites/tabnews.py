import os
from typing import Optional
import requests

import utils
from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()


class TabNews(WebSite):

    __website_name: str = 'TabNews'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'TabNews({super().__repr__()})'

    @property
    def get_website_name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._TabNews__website_name

    def execute(self, limit_pages: int = 10) -> None:

        page: int = 1
        name: str = 'arquivo_{num_page}.json'

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(page=str(page))
                status_code: int = response.status_code

                if status_code == 200:
                    data_tabnews: list = response.json()

                    items: list = self._generate_information(data_tabnews)
                    filename: str = name.format(num_page=page)
                    utils.save_json_file(self._base_path, filename, items)

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

        params: dict = {
            'page': page,
            'per_page': '30',
            'strategy': 'new'
        }
        url: str = os.path.join(self._base_url, f'api/v1/contents')
        response: requests.models.Response = requests.get(
            url=url, params=params, cookies=self._cookies, headers=self._headers
        )
        return response

    def _generate_information(self, items: list) -> list:

        data: list = []
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        for item in items:

            publication_date: Optional[str] = item.get('published_at')
            if publication_date is not None:
                publication_date = utils.convert_date(publication_date, date_format)

            update_date: Optional[str] = item.get('updated_at')
            if update_date is not None:
                update_date = utils.convert_date(update_date, date_format)

            author_name: str = item.get('owner_username', '')

            data.append({
                'website_name': self.get_website_name,
                'url': os.path.join(self._base_url, author_name, item.get('slug', "")),
                'author': {
                    'name': author_name if author_name else None,
                    'url': os.path.join(self._base_url, item.get('owner_username', ""))
                },
                'text': {
                    'title': item.get('title'),
                    'summary': None,
                    'publication_date': publication_date,
                    'update_date': update_date,
                    'image': None,
                    'audio': None,
                    'video': None,
                }
            })

        return data
