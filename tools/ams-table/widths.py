import sys;sys.path.insert(0,'tools')
from units import *
f=sys.argv[1]
r=pypdf.PdfReader(f);pg=r.pages[0]
d=pg.get_contents().get_data().decode('latin1')
pre,bl=blocks(d);loose,ks=kids(bl[4]);head,us=units(ks[0])
fonts=pg['/Resources']['/Font']
def decode(fn,hexs):
    fo=fonts[fn].get_object()
    cmap=fo.get('/ToUnicode').get_object().get_data().decode('latin1')
    m={}
    for a,b in re.findall(r'<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]+)>',cmap): m[a.upper()]=bytes.fromhex(b).decode('utf-16-be')
    for a,b,c in re.findall(r'<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]+)>',cmap):
        for i in range(int(a,16),int(b,16)+1): m['%04X'%i]=chr(int(c,16)+i-int(a,16))
    return ''.join(m.get(h.upper(),'?') for h in hexs)
for kind,b,yr in us:
    if kind!='unit' or b[0].strip()!='BT': continue
    fn=b[1].split()[0];size=b[1].split()[1];x=b[2].split()[4]
    tds=sum(float(l.split()[0]) for l in b[3:] if l.split()[-1]=='Tj' and 'Td' in l)
    hexs=re.findall(r'<([0-9A-Fa-f]{4})>',' '.join(b[3:]))
    # width approx: tds + last glyph adv (~8)
    print(yr[0],x,fn,size,round(tds+8),decode(fn,hexs))
