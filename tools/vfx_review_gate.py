import asyncio, json
from playwright.async_api import async_playwright
U='https://eccestanczyk.github.io/dfmc/vfx.html?admin=1'
KEY=open('REVIEW_KEY.txt').read().strip()
R=[]
def chk(n,ok,d=''): R.append(ok); print(('PASS' if ok else 'FAIL'),'|',n,'|',d)

async def boot(ctx):
  pg=await ctx.new_page(); await pg.goto(U,wait_until='networkidle'); await pg.wait_for_timeout(2500); return pg

async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1280,'height':950})
    pg=await boot(ctx)
    a=await pg.evaluate("document.querySelectorAll('#ally .unit').length")
    e=await pg.evaluate("document.querySelectorAll('#enemy .unit').length")
    chk('3 units per side', a==3 and e==3, f'{a}/{e}')
    r1=await pg.evaluate("[...document.querySelectorAll('.unit img')].map(i=>i.src).join()")
    pg2=await boot(ctx); r2=await pg2.evaluate("[...document.querySelectorAll('.unit img')].map(i=>i.src).join()"); await pg2.close()
    chk('teams randomize on refresh', r1!=r2)
    n=await pg.evaluate("document.querySelectorAll('#grid .card').length")
    chk('grid = 300 creatures + class', n==301, f'{n}')
    # real creature (skip Character card)
    await pg.evaluate("document.querySelectorAll('#grid .card')[5].click()"); await pg.wait_for_timeout(500)
    mv=await pg.evaluate("document.querySelectorAll('.mv-btn').length")
    chk('creature opens 4 moves', mv==4, f'{mv}')
    await pg.evaluate("document.querySelectorAll('.mv-btn')[0].click()"); await pg.wait_for_timeout(400)
    same=await pg.evaluate("(()=>{const a=document.querySelector('#ally .unit img').src,e=document.querySelector('#enemy .unit img').src;return a===e})()")
    chk('both leads become selected mon', same)
    seq=await pg.evaluate("""(async()=>{const s=[];const t0=Date.now();
      while(Date.now()-t0<7000){const a=document.querySelector('#ally .unit.lead')?.classList.contains('cast');
      const e=document.querySelector('#enemy .unit.lead')?.classList.contains('cast');
      const v=a?'A':e?'E':null; if(v&&s[s.length-1]!==v)s.push(v); await new Promise(r=>setTimeout(r,60));}return s})()""")
    chk('alternates ally/enemy', len(seq)>=3 and all(seq[i]!=seq[i+1] for i in range(len(seq)-1)), ''.join(seq))
    ill=await pg.evaluate("""(()=>{let bad=[];for(const m of Object.values(MOVE_BY_ID)){const t=legalTargets(m,'ally',0);
      const kinds=(m.Targets||'enemy').split('+').map(s=>s.trim());
      for(const [sd,ix] of t){ const ok=(kinds.includes('enemy')&&sd==='enemy')||(kinds.includes('self')&&sd==='ally'&&ix===0)||(kinds.includes('ally')&&sd==='ally'&&ix!==0);
      if(!ok) bad.push(m.Move_ID+':'+sd+ix);} } return [Object.keys(MOVE_BY_ID).length,bad.slice(0,4)]})()""")
    chk('every move targets legally', not ill[1], f'{ill[0]} moves, bad={ill[1]}')
    # approvals
    await pg.evaluate(f"localStorage.setItem('dfmc_vfx_key',{json.dumps(KEY)})")
    await pg.reload(wait_until='networkidle'); await pg.wait_for_timeout(2500)
    await pg.evaluate("document.querySelectorAll('#grid .card')[5].click()"); await pg.wait_for_timeout(400)
    await pg.evaluate("document.querySelectorAll('.mv-btn')[0].click()"); await pg.wait_for_timeout(300)
    mid=await pg.evaluate("selMove.Move_ID")
    if await pg.evaluate(f"approved.has({json.dumps(mid)})"):
      await pg.evaluate("document.getElementById('approveBtn').click()"); await pg.wait_for_timeout(1500)
    await pg.evaluate("document.getElementById('approveBtn').click()"); await pg.wait_for_timeout(1800)
    import subprocess
    srv=subprocess.run(['curl','-s','--noproxy','*','https://dfmc-vfx.duiliovarella.workers.dev/approvals'],capture_output=True,text=True).stdout
    chk('approval reaches the server', mid in srv, mid)
    ctx2=await b.new_context(); pg3=await boot(ctx2)
    seen=await pg3.evaluate(f"approved.has({json.dumps(mid)})")
    chk('approval visible in a clean browser', seen)
    await pg3.close(); await ctx2.close()
    await pg.evaluate("document.getElementById('clearBacklog').click()")
    pg.on('dialog', lambda d: d.accept())
    await pg.wait_for_timeout(600)
    still=await pg.evaluate(f"approved.has({json.dumps(mid)})")
    chk('approval survives backlog clear', still)
    await pg.evaluate("document.getElementById('approveBtn').click()"); await pg.wait_for_timeout(1200)
    await b.close()
  print('\nSUMMARY',sum(R),'/',len(R))
asyncio.run(main())
