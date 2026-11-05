"""Offline migration check. No model calls, network, or publication."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from health_agent.reference_memory import load_reference_memory


def main():
    inventory = json.loads((ROOT / 'reports/migration-files.json').read_text())
    for name, expected in inventory['files'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('迁移文件缺失或变化：' + name)
    sources, identity = load_reference_memory(ROOT)
    assert identity['count'] == 50 and len(sources) == 100
    assert sum(s['kind'] == 'visual_reference' for s in sources) == 50
    print(json.dumps({'verified_files': len(inventory['files']),
                      'new_reference_posts': identity['count'],
                      'loaded_sources': len(sources),
                      'status': 'PASS', 'live_model_called': False,
                      'publication_attempted': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
