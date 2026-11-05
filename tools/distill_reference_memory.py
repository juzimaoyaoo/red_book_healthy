"""Publish derived editorial rules, never the copyrighted reference full text."""
import collections,json
from pathlib import Path
from health_agent.core import ROOT,atomic_json

RULES=[
 ('topic','n002,n010','用可辨认的冲突提出问题','先写读者正在冲突的两件事，再确定正文要解释或改变哪个判断；不能把所有原因提前排除。','标题中的两边是否都在答案中得到解释？'),
 ('title','n003,n023,n054','数字必须帮读者判断适配','时长、距离、频次、预算均交代统计口径和漏掉的成本；距离筛选后仍需路线、时间和环境条件，不能一个数字包办适配。','承诺的时间、费用或次数怎样算，哪些情况下不成立？'),
 ('content','n016,n017,n019','从组合骨架接到执行顺序','食谱或方案先区分固定组成与可替换项，再给采购/准备/执行入口；多份成品应说明共用哪些步骤，不能只堆菜单。','读者选了一份后，能找到下一步和缺材料时的替代入口吗？'),
 ('content','n003,n020,n021','让清单可选、可查、可回到图片','不同方案标明是任选、递进还是叠加；用同一编号连接图片与食材/条件，不让读者在重复段落里找对应。','这几项是什么关系，每页比上一页新增什么选择依据？'),
 ('visual','n005,n006,n007','图形关系必须与比较维度一致','状态对照保持对象和观察角度一致，把变化集中在局部；分类表醒目标出排序维度，不能让颜色或上下顺序暗示未经证实的风险大小。','对照是否只改变目标变量，读者会把色阶误认为严重程度吗？'),
 ('content','n013,n015','提前回答后，后页要推进判断','核心答案可以提前出现，后页分别增加辨识语言、条件、例子或下一步；不能只换词重复反转，也不能用三个原因名称冒充三种可用判断。','去掉这一页会损失什么具体判断或行动依据？'),
 ('content','n001,n040,n041','把方法放进真实触发点','选外卖标明下单、加购、备注的操作位置；习惯方案连接原本会发生的动作，并给漏做后的恢复入口，不能增加一串完美打卡任务。','读者在什么界面或事件之后做什么，漏做一次如何继续？'),
 ('review','n012,n026,n045','拆开观察、解释和行动','研究关联、候选机制、个人体验及普通人的建议分别核源；论文名、账号认证和热度都不能填补人群、条件、比较及结局信息。','原文是否直接支持这个人群、剂量、因果和结果，还是跨了层级？'),
 ('title','n024,n027,n046','叙事规模与标题承诺一致','首次尝试、个人记录、解释型图解各有价值，标题应让读者准确预期；不把单人感受改写成最佳排名或本号实测，不以强结果替代过程。','公开稿说的是谁、做了几次、观察到什么，是否被扩大成普遍结论？'),
 ('review','n017,n019,n021','实例库与完整计划分开承诺','合集可供选择，但不自动成为营养处方或完整周计划；食材量、保存和复热条件须当轮核源，不能从照片判断实际安全或减重效果。','标题承诺的是灵感、流程还是处方，正文是否超出了证据？'),
]

def main():
    manifest_path=ROOT/'research/reference-new50-20261105/manifest.json'
    manifest=json.loads(manifest_path.read_text());selected=manifest['selected'];ids={x['id'] for x in selected}
    rules=[]
    for number,(stage,anchors,name,rule,question) in enumerate(RULES,1):
        refs=anchors.split(',')
        if not set(refs)<=ids:raise ValueError('规则引用了未入选样本：'+anchors)
        rules.append({'id':f'new50-R{number:02}','stage':stage,'source_ids':['new50-'+x for x in refs],
                      'name':name,'rule':rule,'review_question':question})
    atomic_json(ROOT/'research/reference-new50-20261105/distilled-rules.json',{'rules':rules,'limits':manifest['limits']})
    playbook_path=ROOT/'config/reference-playbook.json';playbook=json.loads(playbook_path.read_text())
    playbook['version']='2026-11-05-new50-memory-v4'
    playbook['evidence_scope']='旧50篇规则回归保留；新增50篇真实模型逐篇图文拆解，非医学核验、非流量效果回测。'
    playbook['new50_learning']={'manifest':str(manifest_path.relative_to(ROOT)),'count':50,
                              'positive_editorial':manifest['usage_counts'].get('positive_editorial',0),
                              'contrast':manifest['usage_counts'].get('contrast',0),'rules':rules,
                              'runtime':'ProductionAgent自动装载，先read_sources；每个选题及成稿均须引用相关正向样本，标题与正文迁移分别说明。'}
    playbook['visual_learning']['new50_scope']='逐篇scope及原图hash见新增manifest；完整正文配首图的案例不宣称全轮播已读。'
    atomic_json(playbook_path,playbook)
    pages=sum(len(x['images']) for x in selected)
    full=sum(len(x['images'])==x['source_image_count'] for x in selected)
    lines=['# 新增50篇参考学习与agent接入',
           '',f"冻结50篇，与旧50按作者标题归一化和实质正文hash去重。候选{len(selected)+len(manifest['excluded'])}篇，剔除/备用{len(manifest['excluded'])}篇。",
           f"作者显示名{len(manifest['author_counts'])}个；正向表达样本{manifest['usage_counts'].get('positive_editorial',0)}篇，反例{manifest['usage_counts'].get('contrast',0)}篇。正向只评价表达结构，不认证医学正确。",
           f"实际提供{pages}张截图；{full}篇采齐标示图片，其余{50-full}篇以完整正文和已读首图为依据。采齐图片仍须以逐篇可读性与缺失说明判断，不等同医学全图终审。",
           '', '## 经验怎样进入生产','',
           '生产入口仍为 `python3 -m health_agent produce --task TASK --packet PACKET --run NEW_RUN`。`config/reference-library.json`固定manifest hash；加载器核原文、图片、拆解版本及旧库身份，作为reference/visual_reference加入来源索引。',
           '每个选题和成稿须实际读源并应用至少一个新增库的相关正向样本，分别记录标题迁移、内容迁移、原创变化及不照搬事项；只挂载文件、不应用会被程序拒绝。医学主张仍只允许引用已读official_fact，反例不作健康建议。',
           '修改库、协议代码或长期标准后必须新建run；不会把旧发布稿追溯改称使用过本轮新样本。',
           '', '## 沉淀的10条规则','']
    for r in rules:
        lines+=['### '+r['id']+' '+r['name'],'',r['rule'], '', '核对：'+r['review_question'], '', '样本：'+', '.join(r['source_ids']),'']
    lines+=['## 50篇逐篇索引','', '|编号|作者|标题|用途|观察范围|','|---|---|---|---|---|']
    for x in selected:
        capture=json.loads((ROOT/x['capture']).read_text())
        lines.append('|'+ '|'.join(str(v).replace('|','／').replace('\n',' ') for v in [x['id'],x['author'],x['title'],x['usable_as'],capture['scope']])+'|')
    lines+=['','## 局限','']+['- '+s for s in manifest['limits']]
    lines+=['','逐篇原文、实际截图、拆解、排除理由与hash留在本地；不对外转载原作者全文或图片。模型批量拆解不等于独立医学盲测，便利样本不能推出本号流量规律。','']
    (ROOT/'reports/reference-new50.md').write_text('\n'.join(lines))
    print(json.dumps({'count':50,'rules':len(rules),'observed_screenshots':pages,'all_marked_images_captured':full},ensure_ascii=False))

if __name__=='__main__':main()
