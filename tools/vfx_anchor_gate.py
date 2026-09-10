import asyncio
from playwright.async_api import async_playwright
R=[]
def chk(n,ok,d=''): R.append(ok); print(('PASS' if ok else 'FAIL'),'|',n,'|',d)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':1000})
    err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
    await pg.goto('https://eccestanczyk.github.io/dfmc/vfx.html?admin=1',wait_until='networkidle')
    await pg.wait_for_timeout(3000)
    # 1: boxOf agrees with the DOM for all six slots
    r=await pg.evaluate("""(()=>{const o=[];
      for(const s of ['ally','enemy']) for(let i=0;i<3;i++){
        const el=document.getElementById(s).children[i], b=boxOf(s,i);
        o.push({s:s,i:i,ok:Math.abs(b.x-(el.offsetLeft+el.offsetWidth/2))<1 &&
                          Math.abs(b.y-(el.offsetTop+el.offsetHeight/2))<1, x:Math.round(b.x), y:Math.round(b.y)});
      } return o;})()""")
    chk('boxOf matches DOM for all six slots', all(x['ok'] for x in r),
        ' '.join(f"{x['s']}{x['i']}({x['x']},{x['y']})" for x in r))
    # 2: an effect aimed at a slot lands inside that slot
    out=await pg.evaluate("""(async()=>{
      const cv=document.getElementById('fx'), g=cv.getContext('2d');
      const dpr=Math.min(2,window.devicePixelRatio||1); const res=[];
      for(const s of ['ally','enemy']) for(let i=0;i<3;i++){
        const from=boxOf(s==='ally'?'enemy':'ally',0), to=boxOf(s,i);
        DFMC_VFX.clear();
        DFMC_VFX.spawn({archetype:'generic_impact',color:'crimson',anchor:'target',
                        duration:'heavy',from:from,to:to,stage:3});
        let best=null;
        for(let f=0;f<10;f++){
          g.clearRect(0,0,cv.width,cv.height);
          DFMC_VFX.render(g, performance.now()+f*40);
          const d=g.getImageData(0,0,cv.width,cv.height).data;
          let n=0,sx=0,sy=0;
          for(let y=0;y<cv.height;y+=4) for(let x=0;x<cv.width;x+=4){
            const a=d[(y*cv.width+x)*4+3]; if(a>24){n++;sx+=x;sy+=y;}
          }
          if(n>20 && (!best||n>best.n)) best={n:n,cx:sx/n/dpr,cy:sy/n/dpr};
        }
        const inside = best && Math.abs(best.cx-to.x)<to.w*0.5 && Math.abs(best.cy-to.y)<to.h*0.5;
        res.push({s:s,i:i,inside:!!inside,dx:best?Math.round(best.cx-to.x):null,dy:best?Math.round(best.cy-to.y):null});
      }
      DFMC_VFX.clear(); return res;})()""")
    for x in out: chk(f"effect lands on {x['s']}{x['i']}", x['inside'], f"offset {x['dx']},{x['dy']}")
    chk('no page errors', not err, '; '.join(err[:2]))
    await b.close()
  print('\nSUMMARY',sum(R),'/',len(R))
asyncio.run(main())
