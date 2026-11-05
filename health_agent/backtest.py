"""Reproducible reference-text regression. Rules and live API modes are separate."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from .core import ROOT, OpenAIClient, Workflow, atomic_json, digest
from .editorial import VERSION, audit_text


def load_cases(dataset, annotations):
    rows = json.loads(Path(dataset).read_text())
    labels = {x['sample_id']: x for x in json.loads(Path(annotations).read_text())}
    seen = set()
    for row in rows:
        key = (row['author'], hashlib.sha256(row['body'].encode()).hexdigest())
        if key in seen:
            raise ValueError('重复正文，不能重复计数')
        seen.add(key)
        if len(row['body']) < 80:
            raise ValueError('短/折叠正文不能计入本组回测')
        label = labels.get(row['sample_id'])
        if not label or key[1] != label['body_sha256']:
            raise ValueError('正文与冻结标注 hash 不一致')
    if len(rows) < 50:
        raise ValueError('本次要求至少50篇，当前样本不足')
    return rows, labels


def run_rules(dataset=ROOT/'data/backtest-50.json', annotations=ROOT/'benchmarks/annotations.json',
              out=ROOT/'reports'):
    rows, labels = load_cases(dataset, annotations)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for row in rows:
        audit = audit_text(row['title'], row['body'])
        observed = {s['code'] for s in audit['signals']}
        label = labels[row['sample_id']]
        missing = sorted(set(label['expected_minimum_rules']) - observed)
        results.append({'sample_id': row['sample_id'], 'title': row['title'], 'author': row['author'],
                        'body_sha256': row['body_sha256'], 'audit': audit,
                        'expected_minimum_rules': label['expected_minimum_rules'], 'missing': missing,
                        'annotation': label['annotation'], 'transferable_mechanic': label['transferable_mechanic'],
                        'baseline_preflight': 'NOT_IMPLEMENTED_IN_V1',
                        'api_evaluated': False, 'clinical_truth_verified': False})
    targeted = [r for r in results if r['expected_minimum_rules']]
    summary = {'mode': 'rules', 'real_unique_articles': len(results),
               'authors': dict(Counter(r['author'] for r in results)),
               'expected_sentinel_cases': len(targeted),
               'fully_matched_sentinel_cases': sum(not r['missing'] for r in targeted),
               'missing_cases': [r['sample_id'] for r in results if r['missing']],
               'rewrite_signals': sum(bool(r['audit']['must_rewrite']) for r in results),
               'api_calls': 0, 'api_status': 'NOT_RUN_NO_KEY_CONFIGURED',
               'generalization_evaluated': False,
               'dataset_sha256': hashlib.sha256(Path(dataset).read_bytes()).hexdigest(),
               'annotations_sha256': hashlib.sha256(Path(annotations).read_bytes()).hexdigest(),
               'rule_version': VERSION,
               'rule_code_sha256': hashlib.sha256((ROOT/'health_agent/editorial.py').read_bytes()).hexdigest(),
               'scope': '真实正文上的样本内规则回归；不是模型API回测、临床真实性评分或流量预测'}
    atomic_json(out/'backtest50-results.json', {'summary': summary, 'articles': results})
    lines = ['# 50篇真实正文回测记录', '',
             '数据源：Mobile MCP 打开每篇笔记并采集可见无障碍正文；正文回测，不包含逐张图片审核。',
             '本次采集62条，剔除12条，冻结50篇。正文和标注均有SHA256。没有编造笔记链接；可按作者+标题在手机回查。', '',
             '## 本次真实完成的范围', '',
             '- 运行50篇去重正文的规则回归，并给每篇记录风险、改法和可迁移结构。',
             '- 42篇有预先指定的最低风险哨兵；命中数：%d/42。未指定哨兵的8篇不是“医学正确”对照。' % summary['fully_matched_sentinel_cases'],
             '- 第一轮最低哨兵覆盖40/42，漏项为s045与s048；扩充繁殖数量/烹饪时长后重跑本文件。第一轮结果保留在backtest50-round1.json。',
             '- v1没有确定性话术预检；v2增加了预检。未运行v1或v2的真实LLM审核，不能将结果解释成模型准确率提升。',
             '- API调用0次：本机没有OPENAI_API_KEY。后续真实API模式已实现，需另行运行，不能冒充已完成。',
             '- 这是依据已读样本设计的样本内回归，没有独立盲测集；不报告泛化精度或流量收益。',
             '- 样本来源分布：' + '；'.join('%s %d篇' % x for x in summary['authors'].items()) + '。60%来自一个账号，存在明显偏差。',
             '- 参考账号和互动数只帮助分析表达；每篇健康稿仍需当轮权威原文核验。', '',
             '## 接入框架的修改', '',
             '1. 选题/制作读取config/reference-playbook.json，采用具体场景、一个优先行动、条件与来源结构。',
             '2. 确定性预检覆盖食物等同药物、保证见效、症状推病因、药物概括、固定睡眠时钟、明星证据、急症归因、热蒸汽、特殊人群、浓度与总量等。',
             '3. 预检覆盖标题、封面、正文、逐页文案；必须改写的信号不能被模型GO越过。普通数值与机制提醒交给独立核源，不等于判错。',
             '4. 即使结果结构损坏，也不能把BLOCKED降为REVISE后自动继续放行。', '',
             '## 规则校准所核原始资料', '',
             '- [NHLBI睡眠阶段](https://www.nhlbi.nih.gov/health/sleep/stages-of-sleep)：周期存在范围，不能拿固定90分钟作为人人适用的保证。',
             '- [NCCIH糖尿病与膳食补充剂](https://www.nccih.nih.gov/health/diabetes-and-dietary-supplements-what-you-need-to-know)：不能把食物/补剂包装成糖尿病药物替代品。',
             '- [NHS气促](https://www.nhs.uk/symptoms/shortness-of-breath/)：气促有多种原因；严重/伴危险症状需要医疗分流，不能统一归因为疲劳。',
             '这些资料只校准部分哨兵，不能声称已经逐项查证50篇的所有医学论断。', '',
             '## 逐篇结果', '',
             '|ID|作者|原题|v2提示|编辑判断与可迁移结构|', '|---|---|---|---|---|']
    for r in results:
        flags = ', '.join(s['code'] for s in r['audit']['signals']) or '无指定模式命中，仍需审核'
        cell = (r['annotation'] + ' 结构：' + r['transferable_mechanic']).replace('|', '／').replace('\n',' ')
        lines.append('|%s|%s|%s|%s|%s|' % (r['sample_id'], r['author'], r['title'].replace('|','／'), flags, cell))
    (out/'backtest50.md').write_text('\n'.join(lines), encoding='utf-8')
    return summary


def run_live(dataset, annotations, out):
    rows, _ = load_cases(dataset, annotations)
    client = OpenAIClient(max_calls=2*len(rows))  # Fail before making success artifacts if no key.
    flow = Workflow(client)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    completed = []
    for row in rows:
        path = out/(row['sample_id']+'.json')
        cache_key = digest({'body': row['body_sha256'], 'title': row['title'], 'prompt': 'reference-live-v1',
                            'model': 'gpt-6.1-sol', 'effort': 'medium'})
        if path.exists():
            old = json.loads(path.read_text())
            if old.get('cache_key') == cache_key and old.get('status') == 'API_COMPLETED':
                completed.append(old)
                continue
        evidence = flow.research('逐项核对这篇参考健康稿的论断、遗漏人群与边界，区分图文正文与图片未见：'
                                 + row['title'] + '\n' + row['body'])
        result = flow.worker('''独立健康内容审核，输出JSON：verdict为REVISE/BLOCKED/NEEDS_MORE_EVIDENCE，
issues为问题列表（每项含claim, reason, source_urls），transferable_structure为可借鉴结构列表。
不能GO：参考稿尚未制作成本账号新稿，图片未审。只用当前证据，来源不足明确说不清楚。
不要参考作者声望或互动数判真实性，不请求内部思维。''',
                             {'title': row['title'], 'body': row['body'], 'evidence': evidence,
                              'preflight': audit_text(row['title'], row['body'])})
        if result.get('verdict') not in ('REVISE','BLOCKED','NEEDS_MORE_EVIDENCE') or not isinstance(result.get('issues'), list):
            raise ValueError('API审核结构不完整，停止，不记完成')
        if not isinstance(result.get('transferable_structure'), list):
            raise ValueError('API缺少可迁移结构')
        for issue in result['issues']:
            if not isinstance(issue, dict) or not all(issue.get(k) for k in ('claim','reason','source_urls')):
                raise ValueError('API问题缺少论断、理由或来源')
            if not set(issue['source_urls']).issubset(evidence['urls']):
                raise ValueError('API问题来源未在当轮原文证据中')
        record = {'sample_id': row['sample_id'], 'cache_key': cache_key, 'status': 'API_COMPLETED',
                  'input_sha256': row['body_sha256'], 'result': result, 'evidence': evidence,
                  'model': 'gpt-6.1-sol', 'effort': 'medium', 'usage': client.usage[-2:]}
        atomic_json(path, record)
        completed.append(record)
        flow.save()
    summary = {'mode':'live', 'completed':len(completed), 'api_requests_this_run':client.calls,
               'status':'API_COMPLETED' if len(completed) >= 50 else 'INCOMPLETE'}
    atomic_json(out/'summary.json', summary)
    return summary
