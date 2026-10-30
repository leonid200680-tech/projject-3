import json
import re
import uuid
from pathlib import Path

from django.conf import settings

DATA_DIR: Path = settings.HEALTH_DATA_DIR
DATA_DIR.mkdir(parents=True, exist_ok=True)

SAFE_RE = re.compile(r'[^A-Za-z0-9_.-]+')


def safe_name(name: str) -> str:
    name = Path(name).name
    name = SAFE_RE.sub('_', name)
    if not name.lower().endswith('.json'):
        name += '.json'
    return name or 'data.json'


def gen_filename() -> str:
    return f'data_{uuid.uuid4().hex[:8]}.json'


def save_records(records: list[dict]) -> Path:
    path = DATA_DIR / gen_filename()
    with path.open('w', encoding='utf-8') as f:
        json.dump({'records': records, 'count': len(records)},
                  f, ensure_ascii=False, indent=2)
    return path


def list_files() -> list[Path]:
    if not DATA_DIR.exists():
        return []
    return sorted(p for p in DATA_DIR.iterdir()
                  if p.is_file() and p.suffix.lower() == '.json')