"""Register a 6x2 transparent sheet into a clean walk loop.
Fixes the clipping: the cell is sized from the WIDEST transformed frame, never cropped."""
import sys, numpy as np
from PIL import Image
src=sys.argv[1] if len(sys.argv)>1 else 'sheet/assassin_25_v2.png'
tag=sys.argv[2] if len(sys.argv)>2 else 'v2'
im=Image.open(src).convert('RGBA'); W,H=im.size; cw,ch=W/6,H/2
fr=[im.crop((int(q*cw),int(r*ch),int((q+1)*cw),int((r+1)*ch))) for r in range(2) for q in range(6)]
def anch(f):
    a=np.asarray(f.getchannel('A'))>40; ys,xs=np.where(a)
    top,bot=ys.min(),ys.max(); h=bot-top
    hd=a[top:top+int(h*0.35),:]; hx=np.where(hd.any(0))[0]
    return top,bot,h,(hx.min()+hx.max())/2, xs.min(), xs.max()
A=[anch(f) for f in fr]
TH=900.0                                   # every figure normalised to this body height
sc=[TH/x[2] for x in A]
# how far left and right of the head anchor does any frame reach, after scaling?
L=max((a[3]-a[4])*s for a,s in zip(A,sc)); R=max((a[5]-a[3])*s for a,s in zip(A,sc))
CW=int((L+R)*1.10); CH=int(TH*1.18)        # 10% side margin, 18% headroom+floor
print(f'cell {CW}x{CH}  (widest reach L{L:.0f} R{R:.0f})')
out=[]
for f,a,s in zip(fr,A,sc):
    g=f.resize((max(1,int(f.width*s)),max(1,int(f.height*s))),Image.LANCZOS)
    px=int(CW*L/(L+R) - a[3]*s); py=int(CH*0.94 - a[1]*s)
    p=Image.new('RGBA',(CW,CH),(0,0,0,0)); p.paste(g,(px,py),g); out.append(p)
# clip check
for i,p in enumerate(out):
    al=np.asarray(p.getchannel('A'))>40
    if al[:,0].any() or al[:,-1].any() or al[0,:].any() or al[-1,:].any():
        print(f'  WARN frame {i} touches an edge')
sheet=Image.new('RGBA',(CW*len(out),CH),(0,0,0,0))
for i,p in enumerate(out): sheet.paste(p,(i*CW,0),p)
sheet.save(f'walk_{tag}_sheet.png')
for nm,d in [(f'walk_{tag}.gif',100),(f'walk_{tag}_slow.gif',190)]:
    fl=[Image.alpha_composite(Image.new('RGBA',p.size,(28,28,30,255)),p).convert('RGB') for p in out]
    fl[0].save(nm,save_all=True,append_images=fl[1:],duration=d,loop=0)
print('wrote', f'walk_{tag}_sheet.png', f'walk_{tag}.gif')
