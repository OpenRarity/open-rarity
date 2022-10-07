from abc import ABC, abstractclassmethod


class ExternalProvider(ABC):
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"  # noqa: E501
    }

    @staticmethod
    @property
    def url():
        pass

    @staticmethod
    @abstractclassmethod
    def fetch_tokens():
        ...
