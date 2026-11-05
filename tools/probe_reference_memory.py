"""A bounded real-model read/transfer probe, never a production approval or publication."""
import json
from health_agent.core import ROOT,atomic_json
from health_agent.production import ProductionAgent,BASE
from health_agent.model_adapter import CodexModel,obj,arr,STR

def main():
    run=ROOT/'data/reference-new50-20261105/integration-probe'
    packet=ROOT/'research/reference-new50-20261105/probe-packet.json'
    atomic_json(packet,{'sources':[]})
    model=CodexModel(run/'calls',max_calls=1)
    agent=ProductionAgent(run,packet,{'request':'验证新增50篇记忆确实进入模型读源与原创迁移；不制作发布稿'},model=model)
    ids=['new50-n016','new50-n019','new50-n024','new50-n040']
    # Probe uses actually selected positive examples, never assumes a requested ID survived curation.
    ids=[sid for sid in ids if sid in agent.sources and agent.sources[sid].get('usable_as')=='positive_editorial']
    if len(ids)<2:raise ValueError('探针缺相关正向来源')
    sources=agent.read_sources({'ids':ids[:4]})
    schema=obj({'applications':arr(obj({'source_id':STR,'observed_quote':STR,'mechanic':STR,
                                     'title_application':STR,'content_application':STR,
                                     'original_transformations':arr(STR),'must_not_inherit':arr(STR)})),
                'medical_evidence_status':STR})
    result=model.complete('memory_integration_probe',BASE+'''只验证已读记忆的使用，不做健康事实认证，不写公开成稿。
逐篇对应输入的正向样本，给出短原文锚点、标题和内容不同层面的迁移、至少两项原创变换及不能继承的结论/亲历。
observed_quote必须连续存在于来源text中。健康事实待当轮权威核源，无医学证据时不得发布。
''',{'sources':sources,'scope':'reference memory integration only'},schema)
    agent.citations(result['applications'])
    if {v['source_id'] for v in result['applications']}!={v['id'] for v in sources}:raise ValueError('记忆未实际应用')
    if any(len(v['original_transformations'])<2 or not v['must_not_inherit'] for v in result['applications']):raise ValueError('原创迁移或边界不足')
    agent.require_memory_application(ids,[dict(v,changed_audience_or_evidence='；'.join(v['original_transformations']),
                                             not_copying='；'.join(v['must_not_inherit'])) for v in result['applications']])
    agent.event('memory_integration_probe',result)
    agent.state['status']='MEMORY_PROBE_COMPLETED';agent.save()
    evidence={'result':result,'model_receipt':model.usage,'status':'MEMORY_PROBE_COMPLETED',
              'publication_allowed':False,'library':agent.state['snapshot']['reference_memory']}
    atomic_json(run/'result.json',evidence)
    atomic_json(ROOT/'reports/reference-new50-integration.json',evidence)
    print(json.dumps({'status':'MEMORY_PROBE_COMPLETED','sources':ids},ensure_ascii=False))

if __name__=='__main__':main()
