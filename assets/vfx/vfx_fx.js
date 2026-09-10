/* ============================================================================
   DFMC — THE BATTLE EFFECT RENDERER. ONE IMPLEMENTATION, TWO CONSUMERS.
   Lifted verbatim from play/app.js (VFX_FX, ~line 560). The BODY IS UNCHANGED:
   the only edit is that `E` is now injected instead of being React.createElement,
   so a page with no React can pass a DOM factory and draw the identical thing.

   The game and the codex review page MUST draw from this file. When they had two
   implementations, approving an effect on the review page approved art players
   never saw — the fifth instance of the built-with-no-reader defect in this repo.

     game :  const VFX_FX = DFMC_VFX_FX.build(React.createElement);
     page :  const VFX_FX = DFMC_VFX_FX.build(DFMC_VFX_FX.dom);

   Pair it with vfx_fx.css — the 17 keyframes these effects animate on.
   Colour and duration tables travel with it so they cannot drift either.
   ============================================================================ */
(function (root) {
  var HEX = {blue:'#18306a',purple:'#3a1a56',crimson:'#600e12',green:'#144820',red:'#6e1212',rust:'#7e3818',bone:'#d8cfc0'};
  var DURMS = {fast:400,standard:600,heavy:800};

  /* React.createElement's signature, backed by real DOM. Handles the style object,
     ignores `key` (React-only), and accepts nested arrays of children. */
  function dom(tag, props) {
    var el = document.createElement(tag), i, k, ch = [].slice.call(arguments, 2);
    if (props) for (k in props) {
      if (k === 'key') continue;
      if (k === 'style') { for (i in props.style) el.style[i] = props.style[i]; }
      else if (k === 'className') el.className = props[k];
      else el.setAttribute(k, props[k]);
    }
    (function add(c) {
      if (c == null || c === false) return;
      if (Array.isArray(c)) { c.forEach(add); return; }
      el.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
    })(ch);
    return el;
  }

  function build(E) {
    const W=ch=>E('div',{style:{position:'absolute',inset:0}},...(Array.isArray(ch)?ch:[ch]));
    const shard=(c,d,ang)=>E('div',{key:'s'+ang,style:{position:'absolute',left:'50%',top:'52%',transform:'rotate('+ang+'deg)'}},E('div',{style:{width:'18px',height:'7px',background:c,clipPath:'polygon(0 50%,25% 0,100% 50%,25% 100%)',animation:'vxOut '+Math.round(d*0.4)+'ms ease-out both'}}));
    const burst=(c,d)=>[0,60,120,180,240,300].map(a2=>shard(c,d,a2));
    const ringEl=(c,d)=>null; // impact-hit circle removed per design — no expanding ring on attacks or support
    const chevs=(c,d,up)=>W([0,1,2].map(i=>E('div',{key:i,style:{position:'absolute',left:(30+i*18)+'%',top:'40%'}},E('div',{style:{width:'26px',height:'26px',background:c,clipPath:up?'polygon(50% 0,100% 100%,50% 72%,0 100%)':'polygon(50% 100%,100% 0,50% 28%,0 0)',animation:(up?'vxRise ':'vxFall ')+d+'ms ease-out both',animationDelay:(i*60)+'ms'}}))));
    const bar=(c,d,delay)=>E('div',{key:'b'+delay,style:{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',transform:'rotate(-38deg)'}},E('div',{style:{width:'120%',height:'10px',background:c,clipPath:'polygon(0 50%,6% 0,94% 0,100% 50%,94% 100%,6% 100%)',animation:'vxSweep '+d+'ms ease-in both',animationDelay:delay+'ms'}}));
    const streaks=(c,d,dir,n,delayStep)=>[...Array(n)].map((_,i)=>E('div',{key:i,style:{position:'absolute',top:(38+i*9)+'%',left:0,right:0}},E('div',{style:{width:(50-i*8)+'px',height:'7px',background:c,animation:(dir>0?'vxStreamR ':'vxStreamL ')+d+'ms ease-out both',animationDelay:(i*(delayStep||55))+'ms'}})));
    return {
      generic_impact:(c,d)=>W([ringEl(c,d)].concat(burst(c,d))),
      melee_slash:(c,d,dir)=>W(E('img',{src:SLASH_ART,alt:'',style:{position:'absolute',left:'50%',top:'50%',width:'150%',
        transform:'translate(-50%,-50%) scaleX('+(dir>0?1:-1)+')',transformOrigin:'50% 50%',pointerEvents:'none',
        animation:'vxSlash '+Math.max(220,Math.round(d*0.55))+'ms cubic-bezier(.2,.7,.3,1) both'}})),
      melee_crush:(c,d)=>W([E('div',{key:'k',style:{position:'absolute',left:'50%',top:0,marginLeft:'-24px'}},E('div',{style:{width:'48px',height:'48px',background:c,clipPath:'polygon(50% 100%,0 30%,20% 0,80% 0,100% 30%)',animation:'vxDrop '+d+'ms cubic-bezier(.5,0,.8,1) both'}})), ringEl(c,d)]),
      pierce_strike:(c,d,dir)=>W(E('div',{style:{position:'absolute',top:'46%',left:'50%',marginLeft:'-55px'}},E('div',{style:{width:'110px',height:'8px',background:c,clipPath:'polygon(0 0,86% 0,100% 50%,86% 100%,0 100%)',transform:dir>0?'none':'scaleX(-1)',animation:(dir>0?'vxJabR ':'vxJabL ')+d+'ms cubic-bezier(.2,.9,.3,1) both'}}))),
      whip_lash:(c,d)=>W(E('div',{style:{position:'absolute',left:'22%',bottom:'32%',transformOrigin:'0% 100%',animation:'vxWhip '+d+'ms ease-in both'}},E('div',{style:{width:'92px',height:'9px',background:c,borderRadius:'5px'}}))),
      charge_impact:(c,d,dir)=>W([E('div',{key:'r',style:{position:'absolute',top:'42%',left:'50%',marginLeft:'-35px'}},E('div',{style:{width:'70px',height:'22px',background:c,clipPath:'polygon(0 50%,18% 0,100% 0,100% 100%,18% 100%)',transform:dir>0?'none':'scaleX(-1)',animation:(dir>0?'vxRushR ':'vxRushL ')+d+'ms ease-in both'}})), ringEl(c,d)]),
      projectile:(c,d,dir)=>W(E('div',{style:{position:'absolute',top:'44%',left:'50%',marginLeft:'-11px'}},E('div',{style:{width:'22px',height:'22px',background:c,clipPath:'polygon(50% 0,100% 50%,50% 100%,0 50%)',animation:(dir>0?'vxStreamR ':'vxStreamL ')+d+'ms linear both'}}))),
      bleed_dot:(c,d)=>W([0,1,2].map(i=>E('div',{key:i,style:{position:'absolute',left:(36+i*13)+'%',top:'38%'}},E('div',{style:{width:'14px',height:'18px',background:c,clipPath:'polygon(50% 0,100% 62%,80% 100%,20% 100%,0 62%)',animation:'vxFall '+d+'ms ease-in both',animationDelay:(i*70)+'ms'}})))),
      poison_dot:(c,d)=>W([0,1,2,3].map(i=>E('div',{key:i,style:{position:'absolute',left:(30+i*13)+'%',bottom:'26%'}},E('div',{style:{width:(10+(i%2)*6)+'px',height:(10+(i%2)*6)+'px',background:c,borderRadius:'50%',animation:'vxRise '+d+'ms ease-out both',animationDelay:(i*60)+'ms'}})))),
      burn_dot:(c,d)=>W([0,1,2].map(i=>E('div',{key:i,style:{position:'absolute',left:(34+i*14)+'%',bottom:'30%'}},E('div',{style:{width:'18px',height:'26px',background:c,clipPath:'polygon(50% 0,100% 60%,78% 100%,22% 100%,0 60%)',animation:'vxRise '+d+'ms ease-out both',animationDelay:(i*80)+'ms'}})))),
      drain:(c,d,dir)=>W(streaks(c,d,-dir,3,80)),
      curse:(c,d)=>W(E('div',{style:{position:'absolute',left:'50%',top:'8%',marginLeft:'-17px'}},E('div',{style:{width:'34px',height:'34px',background:c,transform:'rotate(45deg)',animation:'vxFall '+d+'ms ease-in both'}}))),
      atk_down:(c,d)=>chevs(c,d,false),
      def_down:(c,d)=>W([E('div',{key:'l',style:{position:'absolute',left:'36%',top:'38%'}},E('div',{style:{width:'22px',height:'34px',background:c,clipPath:'polygon(0 0,100% 0,100% 78%,0 100%)',animation:'vxSplitL '+d+'ms ease-out both'}})),E('div',{key:'r',style:{position:'absolute',left:'50%',top:'38%'}},E('div',{style:{width:'22px',height:'34px',background:c,clipPath:'polygon(0 0,100% 0,100% 100%,0 78%)',animation:'vxSplitR '+d+'ms ease-out both'}}))]),
      atk_up:(c,d)=>chevs(c,d,true),
      shield_def_up:(c,d)=>W(E('div',{style:{position:'absolute',left:'50%',top:'34%',marginLeft:'-22px'}},E('div',{style:{width:'44px',height:'52px',background:c,clipPath:'polygon(0 0,100% 0,100% 62%,50% 100%,0 62%)',animation:'vxPulse '+d+'ms ease-out both'}}))),
      heal:(c,d)=>W([0,1,2].map(i=>E('div',{key:i,style:{position:'absolute',left:(32+i*15)+'%',bottom:'30%'}},E('div',{style:{width:'20px',height:'20px',background:c,clipPath:'polygon(38% 0,62% 0,62% 38%,100% 38%,100% 62%,62% 62%,62% 100%,38% 100%,38% 62%,0 62%,0 38%,38% 38%)',animation:'vxRise '+d+'ms ease-out both',animationDelay:(i*80)+'ms'}})))),
      cleanse:(c,d)=>W(E('div',{style:{position:'absolute',left:'22%',right:'22%',bottom:'26%',height:'10px',background:c,animation:'vxWipe '+d+'ms ease-out both'}})),
      speed_up:(c,d,dir)=>W(streaks(c,d,dir,3,50)),
      speed_down:(c,d,dir)=>W(streaks(c,d,dir,2,60).concat([chevs(c,d,false)]))
    };
  }

  root.DFMC_VFX_FX = { build: build, dom: dom, HEX: HEX, DURMS: DURMS,
                       ARCHETYPES: Object.keys(build(dom)) };
})(typeof window !== 'undefined' ? window : globalThis);
