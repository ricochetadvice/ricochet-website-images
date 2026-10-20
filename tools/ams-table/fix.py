import sys;sys.path.insert(0,'tools')
from units import *
from pypdf.generic import NameObject, StreamObject, DecodedStreamObject
SPLIT=408.0; RX_OLD=360.39063; RX_NEW=SPLIT+10.39063; MAXW=768-10-RX_NEW
src,dst=sys.argv[1],sys.argv[2]
r=pypdf.PdfReader(src);w=pypdf.PdfWriter();w.append(r);pg=w.pages[0]
d=pg.get_contents().get_data().decode('latin1')
pre,bl=blocks(d);loose,ks=kids(bl[4]);head,us=units(ks[0])
fonts=pg['/Resources']['/Font']
def widths(fn):
    fo=fonts[fn].get_object();desc=fo['/DescendantFonts'][0].get_object()
    W=desc.get('/W',[]);dw=desc.get('/DW',1000);m={};i=0
    while i<len(W):
        a=int(W[i]);b=W[i+1]
        if isinstance(b,list):
            for j,v in enumerate(b): m[a+j]=float(v)
            i+=2
        else:
            for g in range(a,int(b)+1): m[g]=float(W[i+2])
            i+=3
    return m,float(dw)
def parse(b):
    # returns font line, size, x, y, glyphs [(hex,x)]
    fl=b[1];size=float(fl.split()[1]);tm=b[2].split();x=float(tm[4]);y=float(tm[5])
    gl=[];cx=x
    for l in b[3:]:
        t=l.split()
        if t[-1]!='Tj': continue
        if t[1:3]==['0','Td']: cx+=float(t[0])
        gl.append((re.search(r'<([0-9A-Fa-f]+)>',l).group(1),cx))
    return fl,size,x,y,gl
def emit(fl,y,x0,glyphs):
    out=['%noshift','BT',fl,'1 0 0 -1 %s %s Tm'%(fmt(x0),fmt(y))];prev=None
    for h,gx in glyphs:
        if prev is None: out.append('<%s> Tj'%h)
        else: out.append('%s 0 Td <%s> Tj'%(fmt(gx-prev),h))
        prev=gx
    out.append('ET');return out
def fmt(v): s=('%.5f'%v).rstrip('0').rstrip('.');return s
# state fix: navy right before header-left path
idx_left=next(i for i,(k,b,yr) in enumerate(us) if k=='unit' and b[0].strip().endswith(' m') and b[0].startswith('48 ') and yr and yr[1]-yr[0]==32)
assert us[idx_left-1][0]=='state' and us[idx_left-1][1][0].startswith('.0157 .1216 .2'),us[idx_left-1]
us[idx_left-1]=('state',['.7843 .0627 .1804 RG .7843 .0627 .1804 rg'],None)
hdr_top=us[idx_left][2][0]
new=[];i=0;changed={'rect':0,'path':0,'text':0,'rewrap':0}
rightrows=[]
for k,b,yr in us:
    if k=='state': new.append(('raw',b));continue
    s0=b[0].strip()
    if s0=='BT':
        fl,size,x,y,gl=parse(b)
        if abs(x-RX_OLD)<0.01: rightrows.append(len(new)); new.append(('rt',(fl,size,x,y,gl)));continue
        new.append(('raw',b));continue
    nb=[]
    for l in b:
        t=l.split()
        if t and t[-1]=='re' and len(t)==5:
            x,y,ww,h=t[:4]
            if x=='350' and ww=='418': l='%s %s %s %s re'%(fmt(SPLIT),y,fmt(768-SPLIT),h);changed['rect']+=1
            elif x=='48' and ww=='302': l='48 %s %s %s re'%(y,fmt(SPLIT-48),h);changed['rect']+=1
        elif yr and abs(yr[0]-hdr_top)<0.5 and yr[1]-yr[0]==32 and t and t[-1] in('m','l') and t[0]=='350':
            l='%s %s'%(fmt(SPLIT),' '.join(t[1:]));changed['path']+=1
        nb.append(l)
    new.append(('raw',nb))
# group right-column text runs into rows (consecutive lines 16px apart)
groups=[];
for pos in rightrows:
    fl,size,x,y,gl=new[pos][1]
    if groups and abs(y-groups[-1][-1][1][3]-16)<0.6 and new[groups[-1][-1][0]][1][0]==fl: groups[-1].append((pos,new[pos][1]))
    else: groups.append([(pos,new[pos][1])])
fontcache={};shifts=[]
for g in groups:
    fl=g[0][1][0];size=g[0][1][1];fn=fl.split()[0]
    if fn not in fontcache: fontcache[fn]=widths(fn)
    wm,dw=fontcache[fn]
    adv=lambda h: wm.get(int(h,16),dw)*size/1000
    # build word list with relative positions
    words=[];cur=[]
    for _,(fl_,s_,x_,y_,gl) in g:
        if cur: words.append(cur);cur=[]
        for h,gx in gl:
            if int(h,16)==3:
                if cur: words.append(cur);cur=[]
            else: cur.append((h,gx))
    if cur: words.append(cur)
    # word widths (internal positions relative), space width from font
    spw=adv('0003')
    # use original kerning within word: positions relative to first glyph
    W=[]
    for wd in words:
        x0=wd[0][1];W.append(([(h,gx-x0) for h,gx in wd], wd[-1][1]-x0+adv(wd[-1][0])))
    lines=[[]];lw=0
    for wd,ww in W:
        need=ww if not lines[-1] else lw+spw+ww
        if lines[-1] and need>MAXW: lines.append([]);lw=0;need=ww
        lines[-1].append((wd,ww));lw=need
    dyg=sum(e for b_,e in shifts if g[0][1][3]>b_+0.5)
    if len(lines)!=len(g): shifts.append((g[0][1][3]+16*(len(g)-1), 16*(len(lines)-len(g))))
    y0=g[0][1][3];out=[]
    for li,ln in enumerate(lines):
        cx=RX_NEW;gl=[]
        for wi,(wd,ww) in enumerate(ln):
            if wi: gl.append(('0003',cx)); cx+=spw
            for h,rx in wd: gl.append((h,cx+rx))
            cx+=ww
        out+=emit(fl,y0+dyg+16*li,RX_NEW,gl)
    if len(g)>1: changed['rewrap']+=1
    new[g[0][0]]=('raw',out)
    for pos,_ in g[1:]: new[pos]=('raw',[])
    changed['text']+=len(g)
# header text right (font F17) also at RX_OLD? handled in rightrows (any font) -> fine
def shift_unit(lines):
    if lines and lines[0]=='%noshift': return lines[1:]
    ys=[]
    for l in lines:
        t=l.split()
        if not t: continue
        try:
            if t[-1]=='re': ys+=[float(t[1]),float(t[1])+float(t[3])]
            elif t[-1] in('m','l','Tm'): ys.append(float(t[-2]))
        except: pass
    if not ys or min(ys)<hdr_top or min(ys)>=800: return lines
    lo,hi=min(ys),max(ys);dy=0;grow=0
    for base,extra in shifts:
        if lo>base+0.5: dy+=extra
        elif lo<base<hi and lines[0].split()[-1]=='re': grow+=extra
    if not dy and not grow: return lines
    out=[]
    for l in lines:
        t=l.split()
        if t and t[-1]=='re': out.append('%s %s %s %s re'%(t[0],fmt(float(t[1])+dy),t[2],fmt(float(t[3])+grow)))
        elif t and t[-1]=='Tm': out.append(' '.join(t[:5]+[fmt(float(t[5])+dy),'Tm']))
        elif t and t[-1] in('m','l'): out.append('%s %s %s'%(t[0],fmt(float(t[1])+dy),t[2]))
        elif t and t[-1]=='c':
            v=[float(x) for x in t[:6]]
            out.append(' '.join(fmt(x+(dy if i%2 else 0)) for i,x in enumerate(v))+' c')
        else: out.append(l)
    return out
print('shifts',shifts)
body=[]
for k,v in new:
    # split raw into units again for shifting (raw may hold several BT blocks from emit)
    buf=[]
    for l in v:
        buf.append(l)
        if l.split() and l.split()[-1] in END: body+=shift_unit(buf);buf=[]
    body+=buf
ks[0]=head+body+['Q']
# rebuild block 4
inner=bl[4][1:-1];out4=['q'];kd=0;depth=0;ki=0;skipping=False
for ln in inner:
    s=ln.strip()
    if depth==0 and s!='q': out4.append(ln);continue
    if s=='q':
        if depth==0:
            out4+=ks[ki];ki+=1;skipping=True
        depth+=1;continue
    if s=='Q': depth-=1;continue
out4.append('Q')
bl[4]=out4
data='\n'.join(pre)+'\n'+'\n'.join('\n'.join(b) for b in bl)+'\n'
st=DecodedStreamObject();st.set_data(data.encode('latin1'))
pg[NameObject('/Contents')]=w._add_object(st)
w.write(dst);print(changed)
