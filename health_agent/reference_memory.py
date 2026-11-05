"""Load hash-pinned editorial observations; reference posts never become medical evidence."""
import hashlib
import json
from pathlib import Path


def _read(root, relative, expected):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('参考库路径超出工作区')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('参考库文件变化，请重新冻结并创建新运行：' + relative)
    return json.loads(data)


def load_reference_memory(root, config='config/reference-library.json'):
    """Return sources plus immutable library identity. Missing explicit config means disabled."""
    root = Path(root)
    path = root / config
    if not path.exists():
        return [], None
    settings = json.loads(path.read_text())
    manifest = _read(root, settings['manifest'], settings['sha256'])
    if manifest.get('previous_corpus_sha256'):
        previous = root/'data/backtest-50.json'
        if hashlib.sha256(previous.read_bytes()).hexdigest()!=manifest['previous_corpus_sha256']:
            raise ValueError('旧参考集变化，须重新核新增样本去重')
    entries = manifest['selected']
    if len(entries) != 50 or len({v['id'] for v in entries}) != 50:
        raise ValueError('新增参考库必须有50篇独立样本')
    sources, identities = [], set()
    for item in entries:
        capture = _read(root, item['capture'], item['capture_sha256'])
        result = _read(root, item['analysis'], item['analysis_sha256'])
        learning = result['analysis']
        if learning['usable_as'] not in ('positive_editorial', 'contrast'):
            raise ValueError('被排除样本不能进入参考库')
        if result['source_identity']['source_sha256'] != item['capture_sha256']:
            raise ValueError('拆解并非当前参考版本')
        identity = (capture['author'], capture['title'])
        if identity in identities:
            raise ValueError('参考库重复文章')
        identities.add(identity)
        pages = []
        for relative, expected in item['images'].items():
            image_path = (root / relative).resolve()
            if not image_path.is_relative_to(root.resolve()) or hashlib.sha256(image_path.read_bytes()).hexdigest() != expected:
                raise ValueError('参考图片变化')
            # Frozen receipts retain their capture-machine paths. An explicitly
            # configured original root lets clones verify the same relative file
            # without rewriting historical evidence or accepting basename matches.
            receipt_images = result['source_identity']['images']
            receipt_key = str(image_path)
            if settings.get('capture_root'):
                original_root = Path(settings['capture_root'])
                if not original_root.is_absolute():
                    raise ValueError('参考库原采集根目录必须为绝对路径')
                receipt_key = str(original_root / image_path.relative_to(root.resolve()))
            if receipt_images.get(receipt_key) != expected:
                raise ValueError('图片未由当前拆解读取')
            pages.append(str(image_path))
        sid = 'new50-' + item['id']
        common = {'author': capture['author'], 'url': capture.get('url'),
                  'scope': capture['scope'], 'usable_as': learning['usable_as'],
                  'medical_evidence': False, 'learning': learning}
        sources.append(dict(common, id=sid, kind='reference', title=capture['title'],
                            text=capture['title']+'\n'+capture['body'], corpus='new50-20261105'))
        sources.append(dict(common, id=sid+'-visual', kind='visual_reference',
                            title=capture['title']+'（实际观察图片）',
                            text=learning['visual_observation'], image_paths=pages))
    return sources, {'manifest': settings['manifest'], 'sha256': settings['sha256'],
                     'count': len(entries), 'limits': manifest['limits']}
