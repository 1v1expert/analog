class NotFoundException(Exception):
    pass


class AnalogNotFound(Exception):
    def __init__(self, text, detail=None):
        self.text = text
        self.detail = detail


class ArticleNotFound(Exception):
    def __init__(self, text, detail=None):
        self.text = text
        self.detail = detail


class InternalError(Exception):
    def __init__(self, text, detail=None):
        self.text = text
        self.detail = detail
