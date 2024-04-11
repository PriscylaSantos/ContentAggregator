import os.path
import requests
import utils

from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()



class CanalTech(WebSite):

    __website_name: str =  'Canal Tech'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'CanalTech({super().__repr__()})'
    @property
    def get_website_name(self) -> str:
        return self._CanalTech__website_name

    def execute(self, limit_pages: int = 10) -> None:

        page: int = 1
        name: str = 'arquivo_{num_page}.json'
        pagination: str = ""

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(pagination=pagination)
                status_code: int = response.status_code

                if status_code == 200:
                    data_canaltech: dict = response.json()
                    timeline: dict = data_canaltech.get('data', {}).get('timeline', {})
                    pagination: str = timeline.get('paginacao')

                    items: list = self._generate_information(timeline.get('itens', []))
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

    def _get_url(self, pagination: str) -> requests.models.Response:

        params: dict = {'pagination': pagination}
        url = os.path.join(self._base_url, 'timelines/ultimas/')

        response: requests.models.Response = requests.get(
            url=url, params=params, cookies=self._cookies, headers=self._headers
        )
        return response

    def _generate_information(self, items: list) -> list:

        data: list = []
        date_format = "%d/%m/%Y %H:%M"
        for item in items:

            publication_date: Optional[str] = None
            date: Optinal[str] = item.get('data')
            if date is not None:
                publication_date = utils.convert_date(date, date_format)

            data.append({
                'website_name': self.get_website_name,
                'url': item.get('url'),
                'author': {
                    'name': item.get('autor'),
                    'url': None
                },
                'text': {
                    'title': item.get('titulo'),
                    'summary': None,
                    'publication_date': publication_date,
                    'update_date': None,
                    'image': item.get('imagem', {}).get('url'),
                    'audio': None,
                    'video': None
                }
            })

        return data