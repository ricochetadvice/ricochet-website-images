import sys;sys.path.insert(0,'tools')
from kids import *
END={'f','f*','S','B','B*','b','n','ET'}
STATE={'rg','RG','gs','g','G','k','K','cs','CS','scn','SCN','w','J','j','d'}
def units(k):
    body=k[2:-1]  # after 'q' and cm
    res=[];buf=[];inbt=False
    for ln in body:
        t=ln.split();op=t[-1] if t else ''
        if op=='BT': inbt=True
        if not inbt and not buf and op in STATE: res.append(('state',[ln],None));continue
        buf.append(ln)
        if op=='ET': inbt=False
        if op in END and not inbt:
            ys=[]
            for b in buf:
                bt=b.split()
                if not bt: continue
                o=bt[-1]
                try:
                    if o=='re': y=float(bt[-4]);h=float(bt[-2]);ys+= [y,y+h]
                    elif o in('m','l','Tm'): ys.append(float(bt[-2]))
                    elif o=='c': ys+= [float(bt[-2])]
                except: pass
            res.append(('unit',buf,(min(ys),max(ys)) if ys else None));buf=[]
    if buf: res.append(('unit',buf,None))
    return k[:2],res
if __name__=='__main__':
    d=pypdf.PdfReader(sys.argv[1]).pages[0].get_contents().get_data().decode('latin1')
    pre,bl=blocks(d);loose,ks=kids(bl[4])
    head,us=units(ks[0])
    for kind,b,yr in us:
        if kind=='unit': print(yr, b[0][:40] if b[0].split()[-1]!='BT' else 'TEXT '+b[2])
