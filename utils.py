import importlib

from wsgi import WSGIApplication


def load_application(app_module: str, app_object: str) -> WSGIApplication:
    return WSGIApplication(getattr(importlib.import_module(app_module), app_object))
