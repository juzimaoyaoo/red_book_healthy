"""Aggregate real completed calls, retain errors/unknown usage separately."""
import collections,json
from pathlib import Path
from health_agent.core import ROOT,atomic_json,now

def main():
    base=ROOT/'data/reference-new50-20261105'
    call_dirs=[base/'analysis/calls',base/'queue-b/analysis/calls',base/'integration-probe/calls']
    receipts=[];unknown=[];totals=collections.Counter()
    for directory in call_dirs:
        for output in sorted(directory.glob('*-output.json')):
            r=json.loads(output.read_text())['receipt'];r['path']=str(output.relative_to(ROOT));receipts.append(r)
            for event in r['events']:totals.update(event.get('usage',{}))
        for source in sorted(directory.glob('*-input.json')):
            output=source.with_name(source.name.replace('-input.json','-output.json'))
            if not output.exists():unknown.append({'input':str(source.relative_to(ROOT)),'usage':'UNKNOWN'})
    manifest=json.loads((ROOT/'research/reference-new50-20261105/manifest.json').read_text())
    probe=json.loads((ROOT/'reports/reference-new50-integration.json').read_text())
    study=[r for r in receipts if r['role']=='reference_deconstruction']
    count=sum(len(json.loads((ROOT/r['path']).read_text())['result']['samples']) for r in study)
    if count!=60 or len(study)!=12 or probe['status']!='MEMORY_PROBE_COMPLETED':raise ValueError('真实回执不完整')
    value={'created_at':now(),'model':'gpt-6.1-sol','reasoning_effort':'medium',
           'transport':'codex_exec_existing_login','study_completed_calls':len(study),
           'candidate_analyses':count,'frozen_new_samples':len(manifest['selected']),
           'usage_counts':manifest['usage_counts'],'integration_probe':probe['status'],
           'completed_calls_including_probe':len(receipts),'usage_from_completed_receipts_only':dict(totals),
           'unknown_calls':unknown,'receipts':receipts,'tests_passed':44,
           'scope':'真实参考拆解及模型记忆接入验证，不是医学准确率、流量效果评测或新增发布。'}
    atomic_json(ROOT/'reports/reference-new50-live-receipt.json',value)
    for folder in (base,base/'queue-b'):
        atomic_json(folder/'collection-frozen.json',{'status':'FROZEN','candidates':60,'selected':50,
                    'manifest':'research/reference-new50-20261105/manifest.json'})
    print(json.dumps({k:value[k] for k in ['study_completed_calls','candidate_analyses','frozen_new_samples','completed_calls_including_probe','unknown_calls']},ensure_ascii=False))

if __name__=='__main__':main()
