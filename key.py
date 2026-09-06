# Local chroma key for the boon icons (raws on flat pure green). Hue key over the whole image - a pixel is
# background when its green channel dominates red and blue by more than the object ever does (the prompts
# forbid green on the object) - soft alpha across a narrow band, despill on the edge band, then a trim.
import numpy as np, sys
from PIL import Image
def key(src, dst, t0=40, t1=110, pad=24):
    im=Image.open(src).convert('RGB'); a=np.asarray(im).astype(np.float32)
    r,g,b=a[...,0],a[...,1],a[...,2]
    dom=g-np.maximum(r,b)                    # how much green dominates
    alpha=np.clip(1.0-(dom-t0)/(t1-t0),0,1)  # dom<=t0 -> opaque, dom>=t1 -> gone
    # despill: on any pixel where green still dominates, pull it down to the max of the other two
    over=np.maximum(dom,0); g2=g-over*np.where(alpha<1,1.0,0.65)
    out=np.stack([r,np.clip(g2,0,255),b,alpha*255],-1).astype(np.uint8)
    # trim to the opaque bounding box, keep a margin, square it
    ys,xs=np.where(alpha>0.05); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    y0=max(0,y0-pad); x0=max(0,x0-pad); y1=min(a.shape[0],y1+pad+1); x1=min(a.shape[1],x1+pad+1)
    crop=out[y0:y1,x0:x1]; h,w=crop.shape[:2]; s=max(h,w); sq=np.zeros((s,s,4),np.uint8); oy=(s-h)//2; ox=(s-w)//2; sq[oy:oy+h,ox:ox+w]=crop
    Image.fromarray(sq,'RGBA').save(dst); return (w,h,s, float((alpha<1).mean()), float(((alpha>0)&(alpha<1)).mean()))
for fn in ['incense_burner','bait']:
    print(fn, key('raw/%s.png'%fn, 'cut/%s.png'%fn))
