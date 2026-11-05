"""Independent reviews of actual rendered assets, bound to exact text/image hashes."""
import argparse,json,hashlib
from pathlib import Path
from health_agent.production import ProductionAgent
from health_agent.model_adapter import CodexModel
from health_agent.core import atomic_json,digest,now
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--packet',required=True);p.add_argument('--task',required=True);p.add_argument('--post',required=True);p.add_argument('--assets',required=True);a=p.parse_args()
run=Path(a.run);dest=Path(a.assets)
agent=ProductionAgent(run,a.packet,json.load(open(a.task)),CodexModel(run/'calls',max_calls=60),resume=True)
package=agent.state['packages'][a.post]
images=sorted((dest/'images').glob('*.png'))
if len(images)!=len(package['image_plan']):raise ValueError('图片数与当前方案不一致')
identity={'package_hash':digest(package),'images':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in images}}
previous=dest/'actual-review.json'
if previous.exists():
 old=json.loads(previous.read_text())
 if old.get('identity')==identity:raise ValueError('同一套图文已审，禁止重复抽签求GO；请读取已有结果')
 n=len(list(dest.glob('actual-review-v*.json')))+1
 atomic_json(dest/f'actual-review-v{n}.json',old)
reviews={};topic=agent.topic(a.post)
for stage in ['actual_reader','actual_facts']:
 agent.state['step']+=1
 review=agent.review(stage,package,topic['reference_ids'],sorted({c['source_id'] for c in package['claims']}),images)
 reviews[stage]=review
 agent.event(stage,{'post_id':a.post,'identity':identity,'review':review})
 if review['verdict']!='GO':break
passed=len(reviews)==2 and all(r['verdict']=='GO' for r in reviews.values())
atomic_json(previous,{'identity':identity,'reviews':reviews,'status':'ASSET_REVIEW_GO' if passed else 'REVISE','can_publish':False,'published':False,'time':now(),'remaining':'发布前仍需核当轮平台规则、账号身份、预览及AI标识。'})
print(a.post,'ASSET_REVIEW_GO' if passed else 'REVISE',flush=True)
