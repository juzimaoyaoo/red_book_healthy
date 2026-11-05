"""Freeze exactly fifty complete, new, hash-pinned editorial reference analyses."""
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from health_agent.core import ROOT, atomic_json, now

BASE=ROOT/'data/reference-new50-20261105'
MANIFEST=ROOT/'research/reference-new50-20261105/manifest.json'
# Collection artifacts retained as exclusions, never silently corrected into a completed sample.
EXCLUDE={'n025':'采集器误把AI标识当标题，未完成有效元数据读回',
         'n029':'只有被截断的引子和封面，无完整答案',
         'n035':'科普导向商品推荐，排除营销样本',
         'n039':'带饭内容导向饭盒商品推荐，排除营销样本'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return str(path.relative_to(ROOT))
def norm(text):return re.sub(r'[^\w]','',unicodedata.normalize('NFKC',text).casefold())

def main():
    old=json.loads((ROOT/'data/backtest-50.json').read_text())
    if isinstance(old,dict):old=old.get('samples',old.get('notes',[]))
    seen={(norm(x.get('author','')),norm(x['title'])) for x in old}
    bodies={sha_text(x.get('body',x.get('text',''))) for x in old if x.get('body',x.get('text',''))}
    selected=[];excluded=[];counts=collections.Counter()
    paths=sorted(BASE.glob('**/n[0-9][0-9][0-9]-complete.json'),key=lambda p:p.name)
    for path in paths:
        capture=json.loads(path.read_text());sid=capture['id']
        if sid in EXCLUDE:
            excluded.append({'id':sid,'title':capture['title'],'reason':EXCLUDE[sid]});continue
        ap=path.parent/'analysis'/f'{sid}.json'
        if not ap.exists():raise ValueError('尚未拆解：'+sid)
        result=json.loads(ap.read_text());analysis=result['analysis']
        reason=EXCLUDE.get(sid)
        if result['source_identity']['source_sha256']!=sha(path):raise ValueError('分析版本过期：'+sid)
        if analysis['usable_as']=='exclude':reason=reason or analysis['completeness']
        identity=(norm(capture['author']),norm(capture['title']))
        bh=sha_text(capture['body']) if len(capture['body'])>80 else None
        if identity in seen or bh and bh in bodies:reason=reason or '与旧库或本批重复'
        if counts[capture['author']]>=12:reason=reason or '单作者样本上限'
        if len(selected)>=50:reason=reason or '足额后的备用样本'
        if reason:
            excluded.append({'id':sid,'title':capture['title'],'reason':reason});continue
        seen.add(identity)
        if bh:bodies.add(bh)
        counts[capture['author']]+=1
        images={rel(Path(p)):sha(Path(p)) for p in capture['page_screenshots']}
        selected.append({'id':sid,'title':capture['title'],'author':capture['author'],
                         'theme':capture['theme'],'usable_as':analysis['usable_as'],
                         'capture':rel(path),'capture_sha256':sha(path),
                         'analysis':rel(ap),'analysis_sha256':sha(ap),'images':images,
                         'source_image_count':capture['image_count'],'observed_pages':len(images)})
    if len(selected)!=50:raise ValueError(f'完整且不重复的已分析样本只有{len(selected)}，不足50；候选{len(paths)}')
    limits=['便利样本，不代表健康赛道或点击收藏效果；无曝光分母，不作流量因果归因',
            'positive_editorial仅指表达结构可学；contrast为反例，两者都不是医学事实核验',
            '无真实笔记链接的来源使用作者、标题、无障碍原文及图像hash溯源，不编造URL',
            '正文完整但未采全轮播时，视觉结论仅限已读图片；不称50套全图医学终审']
    value={'created_at':now(),'previous_corpus_sha256':sha(ROOT/'data/backtest-50.json'),
           'selected':selected,'excluded':excluded,'author_counts':dict(counts),
           'theme_counts':dict(collections.Counter(x['theme'] for x in selected)),
           'usage_counts':dict(collections.Counter(x['usable_as'] for x in selected)),
           'limits':limits}
    atomic_json(MANIFEST,value)
    atomic_json(ROOT/'config/reference-library.json',{'manifest':rel(MANIFEST),'sha256':sha(MANIFEST)})
    print(json.dumps({k:value[k] for k in ['author_counts','theme_counts','usage_counts']},ensure_ascii=False))

def sha_text(text):return hashlib.sha256(norm(text).encode()).hexdigest()

if __name__=='__main__':main()
