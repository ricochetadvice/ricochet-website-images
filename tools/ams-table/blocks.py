import pypdf,sys,re
def mul(a,b):
    return [a[0]*b[0]+a[1]*b[2],a[0]*b[1]+a[1]*b[3],a[2]*b[0]+a[3]*b[2],a[2]*b[1]+a[3]*b[3],a[4]*b[0]+a[5]*b[2]+b[4],a[4]*b[1]+a[5]*b[3]+b[5]]
def ap(m,x,y): return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])
def blocks(data):
    lines=data.split('\n'); out=[]; depth=0; cur=None; pre=[]
    for ln in lines:
        s=ln.strip()
        if depth==0 and s!='q':
            pre.append(ln); continue
        if s=='q':
            if depth==0: cur=[]
            depth+=1
        cur.append(ln)
        if s=='Q':
            depth-=1
            if depth==0: out.append(cur); cur=None
    return pre,out
def bbox(blk):
    st=[[1,0,0,1,0,0]]; ys=[]; xs=[]; tm=None
    for ln in blk:
        t=ln.split()
        if not t: continue
        op=t[-1]
        try:
            if op=='q': st.append(st[-1][:])
            elif op=='Q': st.pop()
            elif op=='cm': st[-1]=mul([float(v) for v in t[-7:-1]],st[-1])
            elif op=='re':
                x,y,w,h=[float(v) for v in t[-5:-1]]
                for px,py in [(x,y),(x+w,y+h)]:
                    X,Y=ap(st[-1],px,py);xs.append(X);ys.append(Y)
            elif op in('m','l'):
                X,Y=ap(st[-1],float(t[-3]),float(t[-2]));xs.append(X);ys.append(Y)
            elif op=='Tm':
                X,Y=ap(st[-1],float(t[-3]),float(t[-2]));xs.append(X);ys.append(Y)
            elif op=='Do':
                for px,py in[(0,0),(1,1)]:
                    X,Y=ap(st[-1],px,py);xs.append(X);ys.append(Y)
        except Exception as e: pass
    if not ys: return None
    return (min(xs)/3.125,min(ys)/3.125,max(xs)/3.125,max(ys)/3.125)
if __name__=='__main__':
    d=pypdf.PdfReader(sys.argv[1]).pages[0].get_contents().get_data().decode('latin1')
    pre,bl=blocks(d)
    print('pre',pre)
    for i,b in enumerate(bl):
        bb=bbox(b); print(i,len(b),bb and tuple(round(v) for v in bb), ' | '.join(l for l in b if ('rg' in l or 'Tf' in l))[:90])
