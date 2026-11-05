import json,urllib.request,re
from html.parser import HTMLParser
from pathlib import Path
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ['script','style','noscript']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style','noscript']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
specs=[('fact-activity','WHO Physical activity','https://www.who.int/news-room/fact-sheets/detail/physical-activity/'),('fact-insomnia','NHS Insomnia','https://www.nhs.uk/conditions/insomnia/'),('fact-sleep-stages','NIH NHLBI Sleep stages','https://www.nhlbi.nih.gov/health/sleep/stages-of-sleep'),('fact-diet','北京市卫健委膳食指南解读','https://wjw.beijing.gov.cn/xwzx_20031/xwfb/202610/t20261021_4913349.html'),('fact-leftovers','Food Standards Agency Cooking and reheating','https://www.food.gov.uk/safety-hygiene/cooking-your-food')]
out=[]
for sid,title,url in specs:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35) as r:raw=r.read().decode('utf-8',errors='replace');actual=r.url
  parser=Text();parser.feed(raw);text='\n'.join(parser.parts)
  Path('research/agent-v3/evidence/'+sid+'.txt').write_text(text)
  out.append({'id':sid,'kind':'official_fact','title':title,'url':actual,'retrieved_on':'2026-11-05','text':text,'provenance':'direct HTTPS retrieval with urllib; script/style excluded; full extracted text retained'})
  print(sid,'OK',len(text),flush=True)
 except Exception as e:print(sid,'FAILED',type(e).__name__,flush=True)
Path('research/agent-v3/facts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
