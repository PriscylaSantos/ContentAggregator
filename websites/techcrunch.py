import os
from typing import Optional
import requests
import utils

from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()


class TechCrunch(WebSite):
    __website_name: str = 'TechCrunch'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'TechCrunch({super().__repr__()})'

    @property
    def get_website_name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._TechCrunch__website_name

    def execute(self, limit_pages: int = 10) -> None:

        page: int = 1
        name: str = 'arquivo_{num_page}.json'

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(page=str(page))
                status_code: int = response.status_code

                if status_code == 200:
                    data_techcrunch: list = response.json()

                    items: list = self._generate_information(data_techcrunch)
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
            '_embed': 'true',
            'es': 'true',
            'cachePrevention': '0'
        }
        url: str = os.path.join(self._base_url, 'wp-json/tc/v1/magazine')
        response: requests.models.Response = requests.get(
            url=url, params=params, cookies=self._cookies, headers=self._headers
        )
        return response

    def _generate_information(self, items: list) -> list:

        data: list = []
        date_format = '%Y-%m-%dT%H:%M:%S%z'
        for item in items:
            info = item.get('yoast_head_json', {})

            publication_date: Optional[str] = info.get('article_published_time')
            if publication_date is not None:
                publication_date = utils.convert_date(publication_date, date_format)

            update_date: Optional[str] = info.get('article_modified_time')
            if update_date is not None:
                update_date = utils.convert_date(update_date, date_format)

            author_name: str = info.get('author', '')
            image = info.get('og_image', [])
            url_image = None
            if len(image) > 0:
                url_image = image[0].get('url')

            author_url = None
            graph = info.get('schema', {}).get('@graph', [])
            for g in graph:
                if ('name' in g) and (g.get('name') == author_name):
                    author_url = g.get('url')
                    break

            data.append({
                'website_name': self.get_website_name,
                'url': info.get('og_url'),
                'author': {
                    'name': author_name if author_name else None,
                    'url': author_url
                },
                'text': {
                    'title': info.get('og_title'),
                    'summary': info.get('description'),
                    'publication_date': publication_date,
                    'update_date': update_date,
                    'image': url_image,
                    'audio': None,
                    'video': None,
                }
            })

        return data
