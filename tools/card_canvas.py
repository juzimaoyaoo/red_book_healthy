"""Deterministic typography and schematic primitives; no simulated photos/tests."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,re,os
FONT=os.environ.get('HEALTH_CJK_FONT', '/System/Library/Fonts/PingFang.ttc')
BG='#F5F2E9';INK='#143E38';MUTED='#526D66';LINE='#C6D4C8';GREEN='#DDE9DC';ACCENT='#C76141'
class Card:
 def __init__(self,section,page,total,color=INK):
  self.im=Image.new('RGB',(1080,1440),BG);self.d=ImageDraw.Draw(self.im);self.color=color
  self.text((64,44),'许老师聊健康  /  '+section,26,fill=MUTED)
  self.d.line((64,94,1016,94),fill=color,width=3)
  self.text((64,1373),'原创示意 · 健康科普',23,fill=MUTED)
  self.text((905,1373),f'{page:02d} / {total:02d}',23,fill=MUTED)
 def text(self,xy,s,size=36,fill=INK):
  self.d.text(xy,s,font=ImageFont.truetype(FONT,size),fill=fill)
 def lines(self,s,size,width):
  f=ImageFont.truetype(FONT,size);out=[]
  for para in s.split('\n'):
   line=''
   for c in re.findall(r'（[^）]*）|\d+(?:\.\d+)?(?:[×x]\d+(?:\.\d+)?)*(?:小时|厘米|英寸|分钟|点|[°℃℉CF]*)|[A-Za-z]+(?:[./:-][A-Za-z0-9]+)*|冻水|冰袋|冷藏|保冷|冷源|饭盒|食物|小时|厘米|英寸|[^\n]',para):
    if self.d.textlength(line+c,font=f)>width and line:out.append(line);line=c
    else:line+=c
   out.append(line)
  return out
 def para(self,xy,s,size=34,width=950,gap=14,fill=INK,max_y=1350):
  x,y=xy
  for line in self.lines(s,size,width):
   if y+size>max_y:raise ValueError('Text overflow: '+s[:32])
   self.text((x,y),line,size,fill);y+=size+gap
  return y
 def box(self,rect,fill='white',outline=None,r=24,width=2):
  self.d.rounded_rectangle(rect,radius=r,fill=fill,outline=outline,width=width)
 def arrow(self,a,b,fill=INK,width=5):
  self.d.line((*a,*b),fill=fill,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);r=15
  self.d.polygon([b,(b[0]-r*math.cos(ang-.55),b[1]-r*math.sin(ang-.55)),(b[0]-r*math.cos(ang+.55),b[1]-r*math.sin(ang+.55))],fill=fill)
 def bowl(self,x,y,w=170,h=75,fill=GREEN):
  self.d.rounded_rectangle((x,y,x+w,y+h),radius=20,fill=fill,outline=INK,width=4)
  self.d.ellipse((x,y-15,x+w,y+22),fill=BG,outline=INK,width=3)
 def fridge(self,x,y,w=130,h=210):
  self.box((x,y,x+w,y+h),GREEN,INK,12,4);self.d.line((x,y+h*.32,x+w,y+h*.32),fill=INK,width=3)
  self.d.line((x+w*.14,y+h*.10,x+w*.14,y+h*.23),fill=INK,width=4);self.d.line((x+w*.14,y+h*.46,x+w*.14,y+h*.66),fill=INK,width=4)
 def clock(self,x,y,label,size=70):
  self.d.ellipse((x,y,x+size,y+size),outline=self.color,width=4);self.d.line((x+size/2,y+12,x+size/2,y+size/2,x+size*.74,y+size*.67),fill=self.color,width=4)
  self.text((x+size+18,y+10),label,34,fill=self.color)
 def save(self,path):
  Path(path).parent.mkdir(parents=True,exist_ok=True);self.im.save(path)
