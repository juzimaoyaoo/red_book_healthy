"""Render an agent-authored image plan as original operation schematics.
All main text is copied from the approved plan. No fixed page quota.
"""
import argparse,json,hashlib,shutil
from pathlib import Path
from PIL import Image
from card_canvas import Card,INK,MUTED,GREEN,ACCENT,LINE,BG

def clean(s):return s.replace('\\n','\n')
def graphic(c,pid,n):
 d=c.d
 if pid=='p01' and n==1:
  c.box((64,330,1016,705),'#EBEEE2')
  c.text((90,350),'少量热食',30);c.bowl(115,445,190,75);c.arrow((345,480),(485,480));c.fridge(535,395,100,160)
  d.line((675,355,675,670),fill=LINE,width=3)
  c.text((700,350),'大锅先分装',30);c.bowl(710,408,245,65);c.arrow((830,485),(830,513))
  for x in [705,800,895]:c.bowl(x,535,80,30)
  c.arrow((830,580),(830,600));c.fridge(802,615,55,78)
 elif pid=='p01' and n==2:
  c.box((64,400,400,880),'#EBEEE2')
  c.text((105,422),'保冷袋剖面',29)
  c.box((105,485,360,550),'#AAD7DC',INK,12,3)
  c.bowl(105,620,255,85)
  c.box((105,765,360,830),'#AAD7DC',INK,12,3)
  c.text((130,501),'上方冷源',29)
  c.text((195,640),'冷食',30)
  c.text((130,780),'下方冷源',29)
 elif pid=='p01' and n==3:
  c.box((64,330,1016,725),'#EBEEE2')
  c.bowl(150,450,540,175)
  c.box((180,485,660,600),'#D7BC8D',None,14)
  d.ellipse((180,470,660,510),fill='#D7BC8D')
  for x,y in [(300,505),(490,535),(600,495)]:d.ellipse((x-8,y-8,x+8,y+8),fill=ACCENT)
  d.line((490,535,730,375),fill=INK,width=8)
  c.box((710,345,925,425),'white',INK,15,4);c.text((735,360),'食品测温',32)
  c.text((170,660),'测食物内部，不是摸饭盒',32)
 elif pid=='p02' and n==1:
  c.box((64,330,1016,745),'#E6E9E8')
  c.clock(90,370,'起床',65)
  c.text((95,475),'固定时间',38)
  c.text((422,375),'放松',38)
  c.box((420,450,650,500),GREEN,INK,8,2)
  for x in [460,510,560,610]:d.line((x,451,x,470),fill=INK,width=2)
  c.text((425,525),'至少1小时',34)
  c.text((755,375),'上床',38)
  c.box((720,450,980,520),'white',INK,18,2);c.text((748,465),'有困意吗？',34)
  c.arrow((850,530),(850,570))
  c.text((725,590),'困了 → 上床',31);c.text((725,650),'不困 → 先放松',29)
 else:
  c.box((64,330,1016,745),'#E6E9E8')
  d.line((175,415,175,685),fill=INK,width=6)
  for y,label in [(405,'先定起床时间'),(515,'给睡前留出放松'),(625,'上床仍要看困意')]:
   d.ellipse((160,y,190,y+30),fill=ACCENT);c.text((230,y-6),label,39)

def sleep_card(c,p,n):
 groups=clean(p['copy']).split('\n\n')
 if n==1:
  c.para((64,280),groups[0],40,950,10,max_y=340)
  for i,(y,group) in enumerate(zip([380,650,920],groups[1:4])):
   c.box((64,y,1016,y+235),'white')
   if i==0:c.clock(115,y+60,'',90)
   elif i==1:
    c.box((105,y+85,245,y+125),GREEN,INK,8,2)
    for x in [125,155,185,215]:c.d.line((x,y+85,x,y+101),fill=INK,width=2)
   else:
    c.d.polygon([(170,y+55),(225,y+112),(170,y+170),(115,y+112)],outline=INK,width=4)
    c.text((154,y+85),'?',42)
   lines=group.splitlines();c.para((295,y+35),lines[0],40,680,12,max_y=y+95)
   c.para((295,y+100),'\n'.join(lines[1:]),33,680,12,max_y=y+230)
  c.para((64,1205),groups[4],25,950,8,max_y=1265)
 else:
  lines=[x for x in clean(p['copy']).splitlines() if x]
  choose=lambda *prefix:next(x for x in lines if x.startswith(prefix))
  c.para((64,280),lines[0],35,950,10,max_y=340)
  c.d.line((107,385,107,805),fill=INK,width=5)
  for y in [375,510,745]:c.d.ellipse((92,y,122,y+30),fill=ACCENT)
  t21=choose('21');t22=choose('22点：','22:00');sleep=choose('有困意');awake=choose('还不困');wake=choose('次日7')
  after21=lines[lines.index(t21)+1]
  c.para((170,365),t21+('\n'+after21 if not after21.startswith('22') else ''),33,840,12,max_y=465)
  c.para((170,495),t22,33,840,10,max_y=545)
  c.box((170,560,540,630),GREEN);c.para((190,577),sleep,30,330,8,max_y=625)
  c.box((560,560,1016,660),GREEN);c.para((580,570),awake,29,416,8,max_y=655)
  c.arrow((570,542),(355,560));c.arrow((570,542),(785,560))
  extras=[x for x in lines[lines.index(awake)+1:lines.index(wake)]]
  if extras:c.para((170,675),'\n'.join(extras),30,840,8,max_y=725)
  nextline=lines[lines.index(wake)+1]
  c.para((170,735),wake.replace('，不因','，\n不因')+('\n'+nextline if nextline.startswith('前一晚') else ''),33,840,10,max_y=835)
  duration='\n'.join([choose('成人平均'),choose('22点到')])
  c.box((64,865,1016,1025),'white');c.para((84,885),duration,32,912,11,max_y=1018)
  helpheading=choose('何时求助','什么时候找医生')
  helptext='\n'.join(lines[lines.index(helpheading):]).replace('，或影响','，\n或影响')
  c.box((64,1050,1016,1250),'#E6E9E8');c.para((84,1070),helptext,31,912,10,max_y=1240)
 c.para((64,1270),clean(p['source_notes']),20,950,5,fill=MUTED,max_y=1350)

def render(package,dest):
 dest=Path(dest);(dest/'images').mkdir(parents=True,exist_ok=True)
 pages=package['image_plan'];pid=package['post_id'];files=[]
 for p in pages:
  n=p['number'];c=Card('带饭操作' if pid=='p01' else '睡眠安排',n,len(pages))
  headline=clean(p['headline']);end=c.para((64,132),headline,62,950,12,max_y=315)
  if end>320:raise ValueError('headline too long')
  if pid=='p02':
   sleep_card(c,p,n)
   f=dest/'images'/f'{n:02d}.png';c.save(f);files.append(f);continue
  graphic(c,pid,n)
  copy=clean(p['copy'])
  lines=copy.splitlines()
  if pid=='p01' and n==2:
   c.para((64,300),lines[0],36,950,10,max_y=380)
   split=next(i for i,line in enumerate(lines) if line.startswith('到公司'))
   c.para((450,410),'\n'.join(lines[1:split]),33,566,12,max_y=890)
   tail=next((i for i,line in enumerate(lines) if line.startswith('依据')),len(lines))
   c.box((64,930,1016,1195),'white')
   c.para((84,950),'\n'.join(lines[split:tail]),32,912,11,max_y=1185)
   c.para((64,1215),'\n'.join(lines[tail:]),22,950,6,fill=MUTED,max_y=1268)
  elif pid=='p01' and n==1:
   c.para((64,265),lines[0],42,950,10,max_y=325)
   tail=next((i for i,line in enumerate(lines) if line.startswith('依据')),len(lines))
   c.para((64,755),'\n'.join(lines[1:4]),33,950,10,max_y=905)
   c.box((64,920,1016,1190),'white')
   c.para((84,943),'\n'.join(lines[4:tail]),34,912,14,max_y=1180)
   c.para((64,1215),'\n'.join(lines[tail:]),22,950,6,fill=MUTED,max_y=1268)
  else:
   y=c.para((64,760),copy,33,950,10,max_y=1245)
  c.para((64,1280),clean(p['source_notes']),20,950,5,fill=MUTED,max_y=1350)
  f=dest/'images'/f'{n:02d}.png';c.save(f);files.append(f)
 (dest/'package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2))
 (dest/'title.txt').write_text(package['title'])
 (dest/'body.txt').write_text(clean(package['body'])+'\n\n'+' '.join('#'+t.lstrip('#') for t in package['tags']))
 (dest/'render-manifest.json').write_text(json.dumps({'renderer':'tools/render_agent_cards.py','normalization':'literal \\n rendered as line breaks; wording unchanged','image_count':len(files),'images':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},ensure_ascii=False,indent=2))
 thumbs=[]
 for f in files:
  im=Image.open(f);im.thumbnail((360,480));thumbs.append(im)
 board=Image.new('RGB',(360*len(thumbs),480),'white')
 for i,im in enumerate(thumbs):board.paste(im,(360*i,0))
 board.save(dest/'contact-sheet.png')
 return files
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('dest');a=p.parse_args();print([str(x) for x in render(json.load(open(a.package)),a.dest)])
