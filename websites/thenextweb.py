import os
from typing import Optional
import bs4
import requests
import utils

from websites import WebSite
from logger import LoggerConfig
_LOGGER = LoggerConfig('scraper').get_logger()


class TheNextWeb(WebSite):
    __website_name: str = 'TNW'

    def __init__(self, base_url, base_path, headers, cookies):
        super().__init__(base_url, base_path, headers, cookies)

    def __repr__(self):
        return f'TheNextWeb({super().__repr__()})'

    @property
    def get_website_name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._TheNextWeb__website_name

    def execute(self, limit_pages: int = 10) -> None:
        page: int = 1
        name: str = 'arquivo_{num_page}.json'

        try:
            while page <= limit_pages:
                response: requests.models.Response = self._get_url(page=str(page))
                status_code: int = response.status_code

                if status_code == 200:
                    data_thenext = self._get_information(response.text)
                    filename = name.format(num_page=page)
                    utils.save_json_file(self._base_path, filename, data_thenext)
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

        params: dict = {'page': page}
        url: str = os.path.join(self._base_url, 'latest/page', f"{page}/json")
        response: requests.models.Response = requests.get(
            url=url, params=params, cookies=self._cookies, headers=self._headers
        )
        return response

    def _get_information(self, html) -> list:

        infos: list = []
        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, 'html.parser')

        tags = soup.find_all(name='article', attrs={"class": "c-listArticle"})
        if len(tags) == 0:
            tags = soup.find_all(name='article', attrs={"class": '\\"c-listArticle\\"'})

        for tag in tags:

            href: str = tag.h2.a.attrs.get('href')
            href = href.replace("\\", "")
            if href.startswith("/"):
                href = href[1:]
            elif href.startswith(""):
                href = href[2:-1]

            url = os.path.join(self._base_url, href)
            response: requests.models.Response = requests.get(url=url, cookies=self._cookies, headers=self._headers)
            status_code: int = response.status_code

            if status_code != 200:
                _LOGGER.error(
                    f'Error fetching data from url: {response.url}, status_code: {status_code}'
                )
                continue

            data: dict = self._generate_information(response.text)
            data['url']: str = url
            infos.append(data)

        return infos

    def _generate_information(self, text: str) -> dict:

        page: bs4.BeautifulSoup = bs4.BeautifulSoup(text, 'html.parser')

        author = page.find('article', attrs={'id': 'articleOutput'})
        author_url = author.aside.a.attrs.get('href', '')
        if author_url.startswith("/"):
            author_url = author_url[1:]

        header_text = page.find('div', attrs={'class': 'c-header__text'})

        date_format = '%Y-%m-%dT%H:%M:%S%z'
        publication_date: Optional[str] = (
            page.find('meta', attrs={'property': "article:published_time"}).attrs.get('content')
        )
        if publication_date is not None:
            publication_date: str = utils.convert_date(publication_date, date_format)

        modified_time: Optional[bs4.element.Tag] = page.find('meta', attrs={'property': "article:modified_time"})
        update_date: Optional[str] = modified_time.attrs.get('content')
        if update_date is not None:
            update_date = utils.convert_date(update_date, date_format)

        iframe = (
            page.find('div', attrs={'class': 'o-page'}).article.find(
                'div', attrs={'class': 'c-article__main max-lg:mb-xxl'}
            ).p.iframe
        )
        audio = None
        if iframe:
            audio = iframe.attrs.get('src')

        image = page.find('figure', attrs={'class': 'o-media o-media--16:9'})

        data: dict = {
            'website_name': self.get_website_name,
            'author': {
                'name': author.aside.a.attrs.get('data-event-label'),
                'url': os.path.join(self._base_url, author_url)
            },
            'text': {
                'title': header_text.h1.text.strip(),
                'summary': header_text.p.text.strip(),
                'publication_date': publication_date,
                'update_date': update_date,
                'image': image.img.attrs.get('data-src'),
                'audio': audio,
                'video': None
            }
        }

        return data
