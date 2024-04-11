from logger import LoggerConfig
import os
import utils
from websites import CanalTech, GizModo, Globo, OlharDigital, TabNews, TechCrunch, TechTudo, TheNextWeb

_LOGGER = LoggerConfig('scraper').get_logger()

_LIMIT_PAGES = 5
_JSON_FOLDER = os.path.join(os.getcwd(), 'json_files')


def create_folder(name):
    base_path = os.path.join(_JSON_FOLDER, name)
    os.makedirs(base_path, exist_ok=True)
    return base_path


def canal_tech():
    website = CanalTech(
        base_url="https://i.canaltech.com.br",
        base_path=create_folder('canaltech'), headers=utils.HEADERS_CANALTECH, cookies=utils.COOKIE_CANALTECH
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def giz_modo():
    website = GizModo(
        base_url="https://gizmodo.uol.com.br",
        base_path=create_folder('gizmodo'), headers=utils.HEADERS_GIZMODO, cookies=utils.COOKIE_GIZMODO,
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def globo():
    website = Globo(
        base_url=(
            "https://falkor-cda.bastian.globo.com"
        ),
        base_path=create_folder('globo'), headers=utils.HEADERS_GLOBO, cookies=utils.COOKIE_GLOBO,
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def olhar_digital():
    website = OlharDigital(
        base_url="https://olhardigital.com.br",
        base_path=create_folder('olhardigital'), headers=utils.HEADERS_OLHARDIGITAL, cookies=utils.COOKIE_OLHARDIGITAL
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def tabnews():
    website = TabNews(
        base_url="https://www.tabnews.com.br",
        base_path=create_folder('tabnews'), headers=utils.HEADERS_TABNEWS, cookies=utils.COOKIE_TABNEWS,
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def tech_crunch():
    website = TechCrunch(
        base_url="https://techcrunch.com",
        base_path=create_folder('techcrunch'), headers=utils.HEADERS_TECHCRUNCH, cookies=utils.COOKIE_TECHCRUNCH
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def tech_tudo():
    website = TechTudo(
        base_url="https://falkor-cda.bastian.globo.com",
        base_path=create_folder('techtudo'), headers=utils.HEADERS_TECHTUDO, cookies=utils.COOKIE_TECHTUDO
    )
    website.execute(limit_pages=_LIMIT_PAGES)


def thenextweb():
    website = TheNextWeb(
        base_url="https://thenextweb.com",
        base_path=create_folder('thenextweb'), headers=utils.HEADERS_THENEXTWEB, cookies=utils.COOKIE_THENEXTWEB
    )
    website.execute(limit_pages=_LIMIT_PAGES)


if __name__ == '__main__':

    _LOGGER.info('--------- Starting scraper ---------')

    _LOGGER.info('Scraping the Canal Tech website.')
    canal_tech()

    _LOGGER.info('Scraping the Giz Brasil website.')
    giz_modo()

    _LOGGER.info('Scraping the G1-Tecnologia website.')
    globo()

    _LOGGER.info('Scraping the Olhar Digital website.')
    olhar_digital()

    _LOGGER.info('Scraping the TabNews website.')
    tabnews()

    _LOGGER.info('Scraping the TechCrunch website.')
    tech_crunch()

    _LOGGER.info('Scraping the TechTudo website.')
    tech_tudo()

    _LOGGER.info('Scraping the TNW website.')
    thenextweb()

    _LOGGER.info(' --------- Finishing scraper ---------')
