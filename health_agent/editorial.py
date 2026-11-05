"""Deterministic editorial risk sentinels, not a medical truth classifier."""
import json
import re
from pathlib import Path

VERSION = 'editorial-v2.1'
# Hard flags concern the wording/action being promoted, not the author's identity.
RULES = [
 ('food_as_medicine', 'rewrite', r'天然胰岛素|植物胰岛素|替代.{0,6}(?:胰岛素|降糖药)|作用类似胰岛素',
  '不得把普通食物包装为胰岛素或药物替代品。'),
 ('guaranteed_outcome', 'rewrite', r'炎症全部消失|照着吃就能瘦|不反弹|一觉到天亮|立竿见影|效率翻倍|效率更高|免疫力拉满|抗病体质|再也不用数羊',
  '删除普遍见效、疗效保证及未经支持的效果倍数。'),
 ('glucose_promise', 'rewrite', r'越吃血糖越稳|默默稳住你的血糖|妥妥的.{0,5}控糖',
  '不能把单种食物写成稳定血糖的保证。'),
 ('symptom_inference', 'rewrite', r'中[了]?[一二三四五六七八九十两\d]+[个条].{0,20}(?:说明|就该|要注意|戒)|看脸就知道|都是缺钾在捣鬼|下意识小动作都是身体在报警|大概率是脾胃|气血不足|腰椎受损|腐气夹着湿气|积食产生的腐气',
  '症状/行为不能直接确认营养缺乏、病因或诊断。'),
 ('medication_claim', 'rewrite', r'依赖会让身体无法自主分泌|断药反而|强行入睡',
  '区分药物类别、适应证和治疗风险，避免诱导自行停药。'),
 ('sleep_clock', 'rewrite', r'黄金90分钟|(?:\d{1,2}点[—–-]\d{1,2}点).{0,40}(?:修复|清理|排毒)|修复排毒模式',
  '睡眠周期不是人人固定90分钟，也不能从钟点推出固定修复窗口。'),
 ('celebrity_proxy', 'check', r'蔡依林|杨幂|郑钦文|傅园慧|女明星|职业运动员的武器',
  '明星个例不能支撑普通人作息或疗效建议，另查指南。'),
 ('urgent_symptom_framing', 'check', r'心慌冒汗|心跳不规律|突然头晕发黑|爬几层楼梯就气喘|无故控制不住大笑',
  '核急性/持续/严重症状的就医分流，不能一律归因疲劳或缺营养。'),
 ('unsafe_steam', 'rewrite', r'口鼻靠近杯口|吸入水蒸气|吸入.{0,5}蒸汽',
  '热水蒸汽操作需核烫伤风险与证据；不要作为普遍自救建议。'),
 ('intervention_boundary', 'check', r'16\+8|16小时不吃|酸枣仁|重力眼罩|屏住呼吸|养腰动作|拱桥|补充维生素D|薄一点的颈枕|趴睡时',
  '核特殊人群、禁忌、不良反应及停止条件。'),
 ('symptom_exercise_map', 'check', r'对症运动|对症练|专属解救运动',
  '运动方式与某类认知/情绪症状不能一一配对作治疗结论。'),
 ('traditional_diagnosis', 'rewrite', r'寒气湿气全困在体内|都是因为没顺应好天时|冰的吃多了.{0,10}动得太少|寒气.{0,10}越喝越虚',
  '文化性养生说法不能当成现代医学病因诊断或限制饮食的依据。'),
 ('quantity_fallacy', 'rewrite', r'冰块稀释.{0,10}减糖|稀释.{0,15}实际摄入糖分更少',
  '浓度降低不等于摄入总糖量降低，核份量与是否喝完。'),
 ('causal_overreach', 'check', r'越来越笨|越用越笨|器官劳损|六大系统早已持续受损|负担减半',
  '不把一般生活习惯直接说成器官损伤/智力变化，量化疗效另核。'),
 ('study_scope', 'check', r'研究表明|研究发现|科学家做了研究|科学证实|现有的研究|扫描对比|抗炎饮食|帮身体舒缓炎症|大脑在用食物',
  '核研究类型、对象、效应大小、相关与因果；图示不能替代诊断。'),
]


def negated(text, start, end):
    """Narrow clause-local exception; disclaimers elsewhere never cancel a claim."""
    before, after = text[max(0, start-12):start], text[end:end+10]
    return bool(re.search(r'(?:不能|不要|不应|并非|不是|不等于|不存在|不相信|别信|警惕所谓)[^。！？；\n]{0,8}$', before)
                or re.match(r'[”」"\s]*(?:不靠谱|没有依据|并不成立|是误区|不能替代)', after))


def audit_text(title, body, extra=''):
    text = '\n'.join((title, body, extra))
    signals = []
    for code, level, pattern, advice in RULES:
        matches = [m for m in re.finditer(pattern, text) if not negated(text, m.start(), m.end())]
        if matches:
            signals.append({'code': code, 'level': level, 'reason': advice,
                            'matches': [m.group()[:50] for m in matches[:3]]})
    # Flag measurable health claims, but not every numbered list or time-management tip.
    if (re.search(r'\d+(?:\.\d+)?\s*(?:[%％℃]|毫克|μg|mg|公斤|千克|克|ml|毫升)', text, re.I)
            or re.search(r'(?:推荐摄入|推荐|研究|压力|肌肉流失|细菌).{0,40}\d+', text)
            or (re.search(r'\d+\s*只', text) and re.search(r'繁殖|数据', text))
            or (re.search(r'\d+(?:[～—–-]\d+)?\s*(?:分钟|小时)', text)
                and re.search(r'细菌|全熟|杀灭|烹饪|冷藏|危险温区', text))):
        signals.append({'code': 'numeric_claim', 'level': 'check',
                        'reason': '数值需原始来源、单位、适用人群及条件，不能因引用账号知名而免核。', 'matches': []})
    return {'version': VERSION, 'signals': signals,
            'must_rewrite': [s['code'] for s in signals if s['level'] == 'rewrite'],
            'status': 'REVISE' if any(s['level'] == 'rewrite' for s in signals) else 'NEEDS_EVIDENCE_REVIEW',
            'medical_accuracy_verified': False}


def audit_content(content):
    extra = '\n'.join(str(s.get('heading', '')) + '\n' + str(s.get('text', ''))
                      for s in content.get('slides', []) if isinstance(s, dict))
    return audit_text(content.get('title', ''), content.get('body', ''),
                      content.get('cover_text', '') + '\n' + extra)


def reference_playbook(root):
    path = Path(root) / 'config/reference-playbook.json'
    return json.loads(path.read_text()) if path.exists() else {}
