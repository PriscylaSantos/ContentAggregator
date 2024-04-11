from abc import abstractmethod


class WebSite:

    __website_name = ''

    def __init__(self, base_url, base_path,  headers, cookies):

        self._base_url: str = base_url
        self._base_path: str = base_path
        self._headers: dict = headers
        self._cookies: dict = cookies

    def __str__(self):
        return (f'The base_url is {self._base_url}, the base_path is {self._base_path}, the headers is {self._headers} '
                f'and the cookies is {self._cookies}')

    def __repr__(self):
        return f'Website({self._base_url}, {self._base_path}, {self._headers}, {self._cookies})'

    @abstractmethod
    def get_website_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(self, limit_pages: int = 10):
        raise NotImplementedError
