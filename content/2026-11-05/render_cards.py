import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
FONT='/System/Library/Fonts/PingFang.ttc'
W,H=1080,1440
BG='#F6F3E9';INK='#183F35';MUTED='#596B60';ACCENT='#D67742';PALE='#E6EBDF';WHITE='#FFFEF9'

def font(size):return ImageFont.truetype(FONT,size,index=0)
def lines(draw,text,f,width):
 out=[]
 for paragraph in text.split('\n'):
  if not paragraph:out.append('');continue
  line=''
  for c in paragraph:
   if draw.textlength(line+c,font=f)>width and line:
    
    if c in '，。；：？！、）】》,.!?;:%' and len(line)>1:
     out.append(line[:-1]);line=line[-1]+c
    else:
     out.append(line);line=c
   else:line+=c
  if line:out.append(line)
 return out

def write(d,text,x,y,size,width,color=INK,space=1.5):
 f=font(size)
 for line in lines(d,text,f,width):
  d.text((x,y),line,font=f,fill=color)
  y+=int(size*space)
 return y

def pill(d,text,x,y,width,color=PALE):
 d.rounded_rectangle((x,y,x+width,y+54),radius=27,fill=color)
 d.text((x+22,y+9),text,font=font(24),fill=INK)

def base(post,index):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.rectangle((64,62,74,99),fill=ACCENT)
 d.text((94,62),'日常活动' if post['slug'].startswith('01') else '日常饮食',font=font(28),fill=MUTED)
 d.text((909,66),'%02d / 05'%index,font=font(24),fill=MUTED)
 return im,d

def footer(d,slide,index):
 source=slide.get('source','')
 y=write(d,source,70,1300,23,940,MUTED,1.4)
 assert y<1390,('footer overflow',source,y)
 d.line((70,1382,1010,1382),fill='#D8DDD1',width=2)
 d.text((70,1395),'许老师聊健康',font=font(22),fill=MUTED)
 d.text((717,1395),'科普依据见笔记正文',font=font(22),fill=MUTED)

def render(post,slide,index):
 im,d=base(post,index)
 kind=slide.get('kind','body')
 if kind=='cover':
  pill(d,slide['label'],70,153,214)
  y=write(d,slide['heading'],70,265,82,940,INK,1.33)
  write(d,slide.get('text','').split('\n')[0],74,y+50,32,930,MUTED)
  if post['slug'].startswith('01'):
   d.rounded_rectangle((70,710,1010,1155),radius=32,fill=INK)
   d.text((127,741),'05',font=font(210),fill=WHITE)
   d.text((430,894),'分钟',font=font(70),fill=WHITE)
   d.text((130,1060),'一小段走路，也可以成为起点',font=font(35),fill='#DDE8D9')
   for k in range(5):
    x=720+(k%2)*77;yy=780+k*47
    d.ellipse((x,yy,x+34,yy+34),fill=ACCENT)
  else:
   d.rounded_rectangle((70,710,1010,1155),radius=32,fill=INK)
   for j,text in enumerate(['主菜，已经选好了','主食，正常搭配','蔬菜，这一份有吗']):
    yy=763+j*117
    d.rounded_rectangle((122,yy,174,yy+52),radius=10,fill=ACCENT if j==2 else '#3E6055')
    if j==2:d.line((132,yy+28,144,yy+39,166,yy+14),fill=WHITE,width=5)
    d.text((205,yy+1),text,font=font(43),fill=WHITE)
  write(d,slide['qualifier'],74,1202,32,930,MUTED)
 else:
  y=write(d,slide['heading'],70,166,54,940,INK,1.35)
  y=max(280,y+40)
  if 'blocks'in slide:
   for i,(heading,text) in enumerate(slide['blocks'],1):
    f=font(35);ls=lines(d,text,f,806)
    card_h=88+len(ls)*52+30
    d.rounded_rectangle((70,y,1010,y+card_h),radius=24,fill=WHITE)
    d.text((98,y+23),'%02d'%i,font=font(27),fill=ACCENT)
    d.text((166,y+20),heading,font=font(35),fill=INK)
    write(d,text,166,y+83,35,806,MUTED,1.48)
    y+=card_h+28
  elif kind=='tracker':
   y=write(d,'这是空白记录卡，不是实测结果。',76,y,30,920,MUTED)+35
   for field in slide['fields']:
    d.rounded_rectangle((70,y,1010,y+190),radius=24,fill=WHITE)
    d.text((105,y+25),field,font=font(34),fill=INK)
    d.line((105,y+135,970,y+135),fill='#D6DDCF',width=3)
    y+=220
  elif kind=='checklist':
   for i,text in enumerate(slide['items'],1):
    ls=lines(d,text,font(37),790)
    hh=52*len(ls)+58
    d.rounded_rectangle((70,y,1010,y+hh),radius=24,fill=WHITE)
    d.text((101,y+24),str(i),font=font(32),fill=ACCENT)
    write(d,text,169,y+23,37,790,INK,1.45)
    y+=hh+28
  assert y<1160,('content overflow',post['slug'],index,y)
  y=write(d,slide.get('note',''),76,max(y+25,1175),28,928,MUTED,1.4)
  assert y<1290,('note overflow',post['slug'],index,y)
 footer(d,slide,index)
 return im

posts=json.loads((ROOT/'posts.json').read_text())
thumbs=[]
for p in posts:
 out=ROOT/p['slug']/'images';out.mkdir(exist_ok=True)
 for i,slide in enumerate(p['slides'],1):
  im=render(p,slide,i);im.save(out/('%02d.png'%i))
  t=im.resize((270,360));thumbs.append(t)
contact=Image.new('RGB',(270*5,360*2),'white')
for n,t in enumerate(thumbs):contact.paste(t,((n%5)*270,(n//5)*360))
contact.save(ROOT/'contact-sheet.png')
print('Rendered',len(thumbs),'cards and contact-sheet.png')
