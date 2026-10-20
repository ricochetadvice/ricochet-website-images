import sys;sys.path.insert(0,'tools')
from tilt import *
import json
def detect(img):
    a=np.array(img.convert('RGBA')).astype(float);al=a[...,3];lum=a[...,:3].mean(-1)
    m=(al>250)&(lum>170)
    ys,xs=np.nonzero(m)
    return [(xs[np.argmin(ys)],ys.min()),(xs.max(),ys[np.argmax(xs)]),(xs[np.argmax(ys)],ys.max()),(xs.min(),ys[np.argmin(xs)])]
def detect2(img):
    # axis-ish quad: use sum/diff extremes
    a=np.array(img.convert('RGBA')).astype(float);lum=a[...,:3].mean(-1);m=(a[...,3]>250)&(lum>170)
    ys,xs=np.nonzero(m);s=xs+ys;d=xs-ys
    return [(xs[np.argmin(s)],ys[np.argmin(s)]),(xs[np.argmax(d)],ys[np.argmax(d)]),(xs[np.argmax(s)],ys[np.argmax(s)]),(xs[np.argmin(d)],ys[np.argmin(d)])]
def fit(img,flat,q0):
    ta=np.array(img.convert('RGBA')).astype(float)
    mk=Image.new('L',img.size,0);ImageDraw.Draw(mk).polygon([tuple(map(float,p)) for p in q0],fill=255);m0=np.array(mk.filter(ImageFilter.MinFilter(11)))>0
    def sc(q): return np.abs(np.array(warp(flat,q,img.size)).astype(float)[...,:3]-ta[...,:3])[m0].mean()
    best=[tuple(map(float,p)) for p in q0];bs=sc(best)
    for step in [2,1,0.5,0.25]:
        for it in range(3):
            imp=False
            for ci in range(4):
                for dx,dy in [(step,0),(-step,0),(0,step),(0,-step)]:
                    q=list(best);q[ci]=(q[ci][0]+dx,q[ci][1]+dy);s=sc(q)
                    if s<bs: bs,best,imp=s,q,True
            if not imp: break
    return best,bs
def compose(img,flat_old,flat_new,q):
    wo=np.array(warp(flat_old,q,img.size)).astype(float);wn=np.array(warp(flat_new,q,img.size))
    diff=(np.abs(wo[...,:3]-wn[...,:3].astype(float)).max(-1)>8)
    mk=Image.fromarray((diff*255).astype('uint8')).filter(ImageFilter.MaxFilter(9))
    # keep only inside page
    pm=Image.new('L',img.size,0);ImageDraw.Draw(pm).polygon(q,fill=255);pm=pm.filter(ImageFilter.MinFilter(5))
    mk=Image.fromarray(np.minimum(np.array(mk),np.array(pm)))
    out=img.convert('RGBA').copy();out.paste(Image.fromarray(wn),(0,0),mk)
    return out
if __name__=='__main__':
    old,fo,fn,dst,mode=sys.argv[1:6]
    img=Image.open(old);flat_o=Image.open(fo);flat_n=Image.open(fn)
    q0=detect(img) if mode=='tilt' else detect2(img)
    import math
    tw=math.dist(q0[0],q0[1]);sc=tw/flat_o.size[0]
    sz=(round(flat_o.size[0]*sc),round(flat_o.size[1]*sc))
    flat_o=flat_o.resize(sz,Image.LANCZOS);flat_n=flat_n.resize(sz,Image.LANCZOS)
    q,s=fit(img,flat_o,q0);print(dst,'quad',q,'score',round(s,2))
    out=compose(img,flat_o,flat_n,q)
    if dst.endswith('.jpg'): out.convert('RGB').save(dst,quality=90)
    else: out.save(dst,optimize=True)
