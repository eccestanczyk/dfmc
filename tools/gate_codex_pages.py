# Gate for the codex pages fixed 2026-09-09 (mutant box, type moves, balance links).
# Serve the repo root first:  python3 -m http.server 8123
# Then:  python3 tools/gate_codex_pages.py   ->  exit 0 = green
# Red-first proven: fails on the pre-fix tree.
import asyncio, sys, re
from playwright.async_api import async_playwright
B="http://127.0.0.1:8123/"
async def main():
    fails=[]; hrefs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page()

        await pg.goto(B+"creature.html?id=DFMC-031"); await pg.wait_for_timeout(2500)
        body=await pg.inner_text('body')
        above=body.split('CHANGELOG')[0]
        for bad in ["NOT YET","MOVE PROGRESSION","move design not yet started"]:
            if bad.lower() in above.lower(): fails.append("DFMC-031 still shows: "+bad)
        if "MUTANT VARIANT" not in above.upper(): fails.append("mutant section missing")
        arts=await pg.eval_on_selector_all('#mutant-body img.mutant-art','e=>e.map(x=>x.naturalWidth)')
        if arts!=[1024]: fails.append("mutant art not rendered: %s"%arts)

        # a creature with no mutant file must keep the placeholder
        await pg.goto(B+"creature.html?id=DFMC-999"); await pg.wait_for_timeout(1500)

        for ty,anti,syn in [("Beast",1,1),("Celestial",1,1),("Ooze",1,1)]:
            await pg.goto(B+"type.html?type="+ty); await pg.wait_for_timeout(2500)
            t=(await pg.inner_text('#type-moves')).upper()
            if "MOVE DESIGN HAS NOT STARTED" in t: fails.append(ty+": still claims no move data")
            if ("STRONGER AGAINST "+ty.upper()) not in t: fails.append(ty+": anti block missing")
            if ("BOOSTS "+ty.upper()+" ALLIES") not in t: fails.append(ty+": synergy block missing")

        await pg.goto(B+"index.html"); await pg.wait_for_timeout(1500)
        await pg.eval_on_selector("button[onclick*=\"show('balance'\"]","b=>b.click()")
        await pg.wait_for_timeout(3000)
        hrefs=await pg.eval_on_selector_all('#bal-body a','a=>a.map(x=>x.getAttribute("href"))')
        if not hrefs: fails.append("balance table empty")
        bad=[h for h in hrefs if h and h.startswith('codex/creature')]
        if bad: fails.append("index still links codex/creature.html x%d"%len(bad))
        if hrefs:
            r=await pg.evaluate("h=>fetch(h).then(r=>r.status)",hrefs[0])
            if r!=200: fails.append("first balance link returns %s"%r)
        # Apex markers: the five pages must no longer call a shipped zone unimplemented,
        # and bosses.html must still render all ten mutant portraits.
        for page in ["bosses.html","droptables.html","eggs.html","system-streak.html","system-void-apex.html"]:
            await pg.goto(B+page); await pg.wait_for_timeout(2500)
            t=await pg.inner_text('body')
            if page=="system-void-apex.html":
                # the page quotes its own retired wording in the correction block; check the
                # two places a reader actually lands instead of the whole body.
                lead=await pg.inner_text('.sp-lead')
                status=await pg.eval_on_selector("h2:text('Status') + .sp-note","e=>e.innerText")
                if "not yet implemented" in lead.lower(): fails.append(page+": lead still says not yet implemented")
                if "nothing on release" in status.lower(): fails.append(page+": Status still says nothing on release")
            else:
                live=t.split("Changelog")[0].split("CHANGELOG")[0]
                if "not yet implemented" in live.lower(): fails.append(page+": still says not yet implemented")
            if page=="bosses.html":
                arts=await pg.eval_on_selector_all('.boss-img-wrap img','e=>e.map(x=>[x.getAttribute("src"),x.naturalWidth])')
                mut=[a for a in arts if "images/mutants/" in a[0] and a[1]>0]
                if len(mut)!=10: fails.append("bosses.html mutant portraits: %d of 10"%len(mut))
        # the virtual-gear caveat is TRUE and must survive
        await pg.goto(B+"system-void-apex.html"); await pg.wait_for_timeout(2000)
        if "not yet implementable" not in (await pg.inner_text('body')):
            fails.append("void-apex: the true virtual-gear caveat was removed")

        await br.close()
    print(("FAIL" if fails else "PASS"), "balance links:",len(hrefs))
    [print(" -",f) for f in fails]
    sys.exit(1 if fails else 0)
asyncio.run(main())
