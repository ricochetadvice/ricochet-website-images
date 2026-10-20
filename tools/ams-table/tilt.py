import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
def corners(t):
    a=np.array(t).astype(float); al=a[...,3]; lum=a[...,:3].mean(-1)
    m=(al>250)&(lum>170)
    ys,xs=np.nonzero(m)
    s=xs+ys; d=xs-ys
    tl=(xs[np.argmin(s)],ys[np.argmin(s)]); br=(xs[np.argmax(s)],ys[np.argmax(s)])
    tr=(xs[np.argmax(d)],ys[np.argmax(d)]); bl=(xs[np.argmin(d)],ys[np.argmin(d)])
    # page rotated: top-left page corner is the topmost point
    top=(xs[np.argmin(ys)],ys[np.argmin(ys)]); bot=(xs[np.argmax(ys)],ys[np.argmax(ys)])
    left=(xs[np.argmin(xs)],ys[np.argmin(xs)]); right=(xs[np.argmax(xs)],ys[np.argmax(xs)])
    return dict(top=top,right=right,bot=bot,left=left)
def coeffs(dst,src):
    # find coeffs mapping dst(output)->src(input)
    A=[];B=[]
    for (x,y),(u,v) in zip(dst,src):
        A.append([x,y,1,0,0,0,-u*x,-u*y]);B.append(u)
        A.append([0,0,0,x,y,1,-v*x,-v*y]);B.append(v)
    return np.linalg.solve(np.array(A,float),np.array(B,float)).tolist()
def warp(flat,quad,size):
    W,H=flat.size
    src=[(0,0),(W,0),(W,H),(0,H)]
    c=coeffs(quad,src)
    return flat.convert('RGBA').transform(size,Image.PERSPECTIVE,c,Image.BICUBIC)
if __name__=='__main__':
    t=Image.open(sys.argv[1]);print(corners(t))
