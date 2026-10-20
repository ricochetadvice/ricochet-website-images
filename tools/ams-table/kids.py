import sys; sys.path.insert(0,'tools')
from blocks import *
def kids(blk):
    # blk lines incl outer q..Q; return (header lines, children list, trailer)
    inner=blk[1:-1]; head=[];kids=[];depth=0;cur=None;loose=[]
    for ln in inner:
        s=ln.strip()
        if depth==0 and s!='q': loose.append((len(kids),ln)); continue
        if s=='q':
            if depth==0: cur=[]
            depth+=1
        cur.append(ln)
        if s=='Q':
            depth-=1
            if depth==0: kids.append(cur)
    return loose,kids
if __name__=='__main__':
    d=pypdf.PdfReader(sys.argv[1]).pages[0].get_contents().get_data().decode('latin1')
    pre,bl=blocks(d)
    for bi in map(int,sys.argv[2:]):
        loose,ks=kids(bl[bi]); print('block',bi,'loose',[l for _,l in loose][:6])
        for i,k in enumerate(ks):
            bb=bbox(k); txt=' '.join(l for l in k if 'rg' in l)[:60]
            print(' ',i,len(k),bb and tuple(round(v) for v in bb),txt)
