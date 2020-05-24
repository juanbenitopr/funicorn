import importlib


def load_application(app_module: str, app_object: str):
    return getattr(importlib.import_module(app_module), app_object)
