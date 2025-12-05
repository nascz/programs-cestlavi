import os
import json

def _appdata_config_path():
    if os.name == 'nt':
        base = os.getenv('APPDATA') or os.path.expanduser('~')
    else:
        base = os.getenv('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')

    cfg_dir = os.path.join(base, 'OCR_Documentos')
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, 'config.json')

def _project_config_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, '.ocr_config.json')


def load_config():
    for path in [_appdata_config_path(), _project_config_path()]:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                continue
    return {}

def save_config(cfg: dict, use_appdata: bool = True):
    path = _appdata_config_path() if use_appdata else _project_config_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return path
    except Exception:
        try:
            path2 = _project_config_path()
            os.makedirs(os.path.dirname(path2), exist_ok=True)
            with open(path2, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            return path2
        except Exception:
            return None
