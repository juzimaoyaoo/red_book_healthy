import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
WHO='https://www.who.int/news-room/fact-sheets/detail/physical-activity/'
GUIDE='https://www.who.int/europe/publications/i/item/9789240014886'
NHS='https://www.nhs.uk/symptoms/shortness-of-breath/'
VEG='https://wjw.beijing.gov.cn/xwzx_20031/xwfb/202610/t20261021_4913349.html'
posts=[{
'slug':'01-five-minute-walk','title':'忙到没空运动，先走这5分钟',
'body':'''下班到家，包还没放下，已经想好今天的运动计划又要取消。

我的建议是，把起步目标缩小到今天真能做到的一次走路。比如5分钟。

这5分钟是一个方便开始的例子，没有“走够就达标”的意思。

WHO强调，动一点好过完全不动，通勤、家务和休闲中的身体活动都算数。

👟 给走路接上一个现成的时间点
午饭后收好餐盒，或者下班走出办公楼，选你最容易安排的一次。找平坦、安全的路线，按自己能承受的速度走。
时间紧，就先少走一点。

📝 先记“做没做”，不用急着评成绩
手机备忘录写下今天走了几分钟、身体感觉怎样。
这份记录用来找合适的时间，别拿它跟别人的步数比。

能稳定安排后，再逐步增加时间和活动量。

普通成年人的周目标可参考WHO建议，每周150—300分钟中等强度有氧活动；还应安排肌肉力量训练。慢走起步也别直接算成中等强度达标。

已有运动限制，按个人方案来。
活动时出现胸痛、异常气促等不适，先停止并就医评估，严重时及时急救。

今天先选一个你能出门的时间点。你更容易安排在午间，还是下班后？''',
'audience':'想开始活动、但日程紧的普通成年人',
'limitations':'5分钟为作者提供的起步安排示例，不是临床剂量、达标量或见效阈值；不取代个体运动评估。',
'tags':['上班族运动','运动入门','减少久坐','日常走路','健康科普'],
'sources':[{'id':'W1','title':'WHO Physical activity','url':WHO,'checked_on':'2026-11-05'},
{'id':'W2','title':'WHO身体活动和久坐行为指南概览','url':GUIDE,'checked_on':'2026-11-05'},
{'id':'W3','title':'NHS Shortness of breath','url':NHS,'checked_on':'2026-11-05'}],
'claims':[{'id':'c1','statement':'动一点好过完全不动，通勤家务休闲活动均计入身体活动。','source_urls':[WHO,GUIDE]},
{'id':'c2','statement':'成年人每周150—300分钟中等强度有氧活动，兼顾肌肉力量训练；低强度慢走不直接等同达标。','source_urls':[GUIDE]},
{'id':'c3','statement':'异常气促需评估，严重气促、胸部紧重等需紧急医疗处理。','source_urls':[NHS]}],
'slides':[
{'kind':'cover','heading':'忙到没空运动\n先走这5分钟','text':'给想开始、却总没空的你','label':'活动起步卡','proof':'5','qualifier':'先开始，再逐步增加','source':'依据 WHO 身体活动指南'},
{'heading':'把走路接在一件事后面','blocks':[
['午间版','收好餐盒后，找条安全路线走一小段。'],
['下班版','走出办公楼，给自己留一小段走路时间。'],
['先选一个','不用两个都做。按自己能承受的速度起步。']],
'note':'5分钟是安排示例，没有“走够就达标”的意思。','source':'行动示例为本账号整理；原则依据 WHO'},
{'heading':'从少量开始，也算开始','blocks':[
['身体活动不只在健身房','通勤、家务和休闲中的活动，都属于身体活动。'],
['先选能安排的一次','找平坦、安全的路线，时间紧可以先少走一点。'],
['把难度往后放','适应以后，再逐步增加时间和活动量。']],
'note':'动一点好过完全不动；避免一开始就照搬别人的量。','source':'WHO · Physical activity / 指南概览'},
{'kind':'tracker','heading':'记一次，找适合你的时间','text':'这是一张空白记录卡，不是实测结果。',
'fields':['今天的时间点','实际走了几分钟','走完身体感觉怎样'],
'note':'记录用来调整安排。身体不舒服，不靠打卡硬撑。','source':'本账号原创记录工具；无疗效承诺'},
{'heading':'五分钟以后，怎么继续','blocks':[
['周目标要另外看','普通成年人可参考每周150—300分钟中等强度有氧活动，并安排力量训练。'],
['慢走起步，逐步增加','这篇帮你开始；低强度慢走不直接等同中等强度达标。'],
['有不适，先停下','胸痛、异常气促等需就医评估；严重时及时急救。已有运动限制，按个人方案。']],
'note':'来源全文在正文末尾｜健康科普，不替代个人诊疗','source':'WHO 指南概览；NHS · Shortness of breath'}
],
},
{
'slug':'02-takeaway-vegetables','title':'点外卖，先把这份蔬菜补上',
'body':'''中午打开外卖，主菜挑好了，米饭也选了，最后一看，蔬菜只有盒子角落的两片。

我建议你下单前多看一眼，套餐里有没有一份能认真吃的蔬菜。

🥬 点单可以这样安排
先看套餐有没有独立蔬菜。有就正常搭配；没有，就看看能否加一份或和同事合点。

清炒油麦菜、西兰花、白菜都可以轮换，按自己吃得下的份量选，不用每顿追着同一种菜点。

🧾 留一句具体备注
“蔬菜少油少盐，能分开的酱汁请另放。”这是点单诉求，商家实际做法会有差别，收到后仍要看一眼。

主食、肉蛋豆类等也照常合理搭配，别把午饭换成只有一盒青菜。

为什么要盯住这一项？
北京市卫健委介绍《中国居民膳食指南（2022）》时建议，餐餐有蔬菜，每天不少于300克，深色蔬菜约占一半。
外卖也应按需购买、注意份量与荤素搭配。

⚠️ 这是一整天的参考，外卖份量还要单独看。
外卖装了多少、菜本身有多少，通常没法从图片准确判断。
午饭加了一份，也不意味着全天已经吃够，其他餐仍要安排蔬菜。

已有医生或营养师给的饮食限制，按个人方案选择。今天先检查蔬菜这一格，别一下给自己加十条任务。

你点外卖时，最容易漏掉哪一类蔬菜？''',
'audience':'日常点外卖、蔬菜安排容易被忽略的普通成年人',
'limitations':'不按盒子或图片估算克数；加一份不等于全天达标；有个体饮食限制按个人方案。',
'tags':['外卖怎么点','上班族午餐','蔬菜搭配','合理膳食','健康科普'],
'sources':[{'id':'V1','title':'北京市卫健委：《中国居民膳食指南（2022）》核心准则','url':VEG,'checked_on':'2026-11-05'}],
'claims':[{'id':'c1','statement':'餐餐有蔬菜，每天不少于300克，深色蔬菜约占一半。','source_urls':[VEG]},
{'id':'c2','statement':'外卖按需购买，注意份量和荤素搭配，可向商家提出少油少盐诉求。','source_urls':[VEG]},
{'id':'c3','statement':'膳食应包含不同食物类别；蔬菜不替代全部主食及肉蛋豆类食物。','source_urls':[VEG]}],
'slides':[
{'kind':'cover','heading':'外卖里的蔬菜\n先补上这一份','text':'主菜选完，看看蔬菜这一格','label':'点单检查卡','proof':'VEG','qualifier':'具体做法，往后看','source':'依据《中国居民膳食指南（2022）》'},
{'heading':'下单前，多检查一格','blocks':[
['有独立蔬菜吗','别只看套餐里“带不带一点绿”。看看有没有一份能认真吃的蔬菜。'],
['没有，再考虑补上','看看能否加一份，或和同事合点。按需要和吃得下的量选。'],
['其他食物照常搭配','主食、肉蛋豆类等合理安排，午饭不用只剩一盒青菜。']],
'note':'先把蔬菜这件事安排上，不用同时改变全部点单习惯。','source':'依据卫健委膳食准则；点单步骤为本账号整理'},
{'heading':'给商家一句具体备注','blocks':[
['可以直接这样写','蔬菜少油少盐，能分开的酱汁请另放。'],
['菜式按偏好轮换','清炒油麦菜、西兰花、白菜等，选自己吃得下的。'],
['收到后仍要看一眼','备注是诉求，实际做法会有差别；按需点单，避免浪费。']],
'note':'清淡、份量和荤素搭配一起考虑。','source':'北京市卫健委 · 膳食准则四、七、八'},
{'kind':'checklist','heading':'“一份”和“一天”要分清','items':['每天不少于300克蔬菜，是全天参考。','深色蔬菜约占一半；餐餐安排蔬菜。','外卖图片和盒子大小，不能准确换算克数。','午饭加一份，不等于其他餐不用吃。'],
'note':'不做“一盒等于300克”的视觉估算。','source':'北京市卫健委 · 膳食准则三'},
{'heading':'今天只做一次点单检查','blocks':[
['选套餐时','确认有没有独立蔬菜；不够再考虑加一份。'],
['决定份量时','按自己需要买，主食和其他食物合理搭配。'],
['安排全天时','其他餐也要有蔬菜。已有个人饮食限制，按医生或营养师方案。']],
'note':'来源全文在正文末尾｜一般膳食科普，非个体食谱','source':'北京市卫健委《中国居民膳食指南》解读'}
]
}]

for p in posts:
 p['format']='carousel';p['voice_source']='dna';p['voice_confidence']='medium'
 p['production_method']='本会话撰稿与原文核验；未调用未配置的gpt-6.1-sol API'
 p['status']='DRAFT_ASSETS_IN_PROGRESS';p['published']=False
 p['cover_text']=p['slides'][0]['heading']
 # Text fields let the existing code inspect every final slide alongside title and body.
 for s in p['slides']:
  if 'blocks'in s:s['text']='\n'.join(h+'\n'+v for h,v in s['blocks'])
  if 'fields'in s:s['text']=s.get('text','')+'\n'+'\n'.join(s['fields'])
  if 'items'in s:s['text']='\n'.join(s['items'])
  s['text']=s.get('text','')+'\n'+s.get('note','')+'\n'+s.get('source','')
 p['content_hash']=hashlib.sha256(json.dumps({k:p[k] for k in ['title','body','slides','claims']},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 d=ROOT/p['slug'];d.mkdir(exist_ok=True)
 (d/'post.json').write_text(json.dumps(p,ensure_ascii=False,indent=2))
 (d/'body.txt').write_text(p['body'])
 (d/'title.txt').write_text(p['title'])
 (d/'cta.txt').write_text(p['body'].split('\n\n')[-1])
 md='# '+p['title']+'\n\n'+p['body']+'\n\n'+' '.join('#'+t for t in p['tags'])+'\n\n## 来源\n\n'
 md+='\n'.join('- [%s](%s)'%(s['title'],s['url']) for s in p['sources'])
 (d/'article.md').write_text(md+'\n')
(ROOT/'posts.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2))
print([(p['title'],len(p['body'])) for p in posts])
