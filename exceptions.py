# exceptions.py

class CrawlerException(Exception):
    pass

class RequestFailedException(CrawlerException):
    pass

class JSONDecodeException(CrawlerException):
    def __init__(self, message, response_text):
        super().__init__(message)
        self.response_text = response_text
