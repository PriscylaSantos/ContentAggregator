import os
from typing import Optional
import bs4
import requests
import utils

from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()


class OlharDigital(WebSite):

    __website_name: str = 'Olhar Digital'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'OlharDigital({super().__repr__()})'

    @property
    def get_website_name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._OlharDigital__website_name

    def execute(self, limit_pages: int = 10) -> None:

        page: int = 1
        name: str = 'arquivo_{num_page}.json'

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(page=str(page))
                status_code: int = response.status_code

                if status_code == 200:
                    data_gizmodo: list = self._get_information(response.text)
                    filename: str = name.format(num_page=page)
                    utils.save_json_file(self._base_path, filename, data_gizmodo)

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

        url: str = os.path.join(self._base_url, 'editorias/noticias/page', f"{page}/")
        response: requests.models.Response = requests.get(
            url=url, cookies=self._cookies, headers=self._headers
        )
        return response

    def _get_information(self, html) -> list:

        infos: list = []
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, 'html.parser')

        for tag in soup.find_all('a', attrs={'class': 'card-post type8 img-effect1'}):

            link: str = tag.attrs.get('href')
            response: requests.models.Response = requests.get(link, cookies=self._cookies, headers=self._headers)
            status_code: int = response.status_code

            if status_code != 200:
                _LOGGER.error(
                    f'Error fetching data from url: {response.url}, status_code: {status_code}'
                )
                continue

            data: dict = self._generate_information(response.text)
            data['url']: str = link
            infos.append(data)

        return infos

    def _generate_information(self, text: str) -> dict:

        page: bs4.BeautifulSoup = bs4.BeautifulSoup(text, 'html.parser')

        author: Optional[bs4.element.Tag] = page.find('span', attrs={'class': 'autor'}).a

        title: Optional[bs4.element.Tag] = page.find('meta', attrs={'property': 'og:title'}).attrs.get('content')
        summary: Optional[str] = page.find('meta', attrs={'property': 'og:description'}).attrs.get('content')

        date_fromat = '%Y-%m-%dT%H:%M:%S%z'
        publication_date: Optional[str] = (
            page.find('meta', attrs={'property': 'article:published_time'}).attrs.get('content')
        )
        if publication_date is not None:
            publication_date: str = utils.convert_date(publication_date, date_fromat)

        modified_time: Optional[bs4.element.Tag] = page.find('meta', attrs={'property': 'article:modified_time'})
        update_date: Optional[str] = modified_time.attrs.get('content')
        if update_date is not None:
            update_date = utils.convert_date(update_date, date_fromat)

        image: Optional[bs4.element.Tag] = page.find('meta', attrs={'property': 'og:image'}).attrs.get('content')

        data: dict = {
            'website_name': self.get_website_name,
            'author': {
                'name': author.text.strip(),
                'url': author.attrs.get('href')
            },
            'text': {
                'title': title,
                'summary': summary,
                'publication_date': publication_date,
                'update_date': update_date,
                'image': image,
                'audio': None,
                'video': None
            }
        }

        return data
