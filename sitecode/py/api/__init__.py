import json
import importlib

def handle(*section_path, **kwargs):
    module_name = f"sitecode.py.api.{'.'.join(section_path)}"
    endpoint = importlib.import_module(module_name)
    return endpoint.process_request(**kwargs)
