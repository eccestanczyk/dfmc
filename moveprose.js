/* Move descriptions as the game writes them. */
(function(){
const L10N={dat:null,ver:0,code:'en'};
const tx=(k,en)=>en;
const txp=(k,en,...v)=>String(en).replace(/\{v(\d)\}/g,(m,d)=>{ const x=v[d-1]; return x==null?'':String(x); });
const tl=s=>s;
const FXP_N=n=>(+n===1?tx('fxp_one_turn','1 turn'):txp('fxp_n_turns','{v1} turns',n));
const FXP_SPD=(sg,n)=>(sg==='+'?txp('fxp_spd_buff','+{v1} Speed buff',n):txp('fxp_spd_debuff','-{v1} Speed debuff',n));
let _fxpRe=null, _fxpReV=-1;
function fxpNamesIn(s){ s=String(s); if(!L10N.dat) return s; const o=fxpStatusNames();
  if(_fxpReV!==L10N.ver){ const ks=Object.keys(o).sort((x,y)=>y.length-x.length).map(k=>k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')); _fxpRe=ks.length?new RegExp('(?<![\\w-])('+ks.join('|')+')(?![\\w-])','g'):null; _fxpReV=L10N.ver; }
  return _fxpRe?s.replace(_fxpRe,w=>o[w]||w):s; }
const fxpKinIn=s=>fxpNamesIn(s).replace(/\b([A-Z][a-z]+(?: and [A-Z][a-z]+)?)(?= (?:targets?|allies|ally)\b)/g,w=>fxpName(w));
function fxpTail(s){ return fxpKinIn(s)
  .replace(/(\d+)t\b/g,(m,n)=>FXP_N(n))
  .replace(/\breduced Speed stages?\b/g,()=>tx('fxp_reduced_spd','reduced Speed debuff'))
  .replace(/([+-])(\d+) Speed stages?/g,(m,sg,n)=>FXP_SPD(sg,n))
  .replace(/\bvs\b/g,()=>tx('fxp_against','against')).replace(/\s+—\s+/g,', ').replace(/\s{2,}/g,' ').trim(); }
const FXP_STAT=st=>tl(st);
let _fxpSt=null, _fxpStV=-1;
function fxpStatusNames(){ if(_fxpSt&&_fxpStV===L10N.ver) return _fxpSt; const o={}, d=L10N.dat||{};
  for(const k in d){ if(k.indexOf(': ')<0) continue; const a=k.replace(/\.$/,'').split(/\s*;\s*/), b=String(d[k]).split(/\s*[;\uFF1B]\s*/); if(a.length!==b.length) continue;
    for(let i=0;i<a.length;i++){ const e=a[i].match(/^([A-Z][^:;,()]*?): /)||a[i].match(/\b(?:applies|gains|gets|take) ([A-Z][^:;,()]*?): /); if(!e||/ allies$/.test(e[1])||(e[1] in o)) continue;
      const q=b[i].match(/[\u201E\u201C"\u300C\u300E\u00AB][^\u201C\u201D"\u300D\u300F\u00BB]+[\u201C\u201D"\u300D\u300F\u00BB]/g), t=b[i].match(/^([^:\uFF1A]+?)\s*[:\uFF1A]/);
      const v=(q&&q.length===1)?q[0].slice(1,-1):((t&&a[i].indexOf(e[1]+': ')===0)?t[1]:((t&&(t[1].match(/が([^がにを、]+?)を付与/)||t[1].match(/(?:附加|施加)([^，。]+)$/)))||[])[1]||''); if(v) o[e[1]]=v.replace(/^[\u201E\u201C"\u300C\u300E]+|[\u201C\u201D"\u300D\u300F]+$/g,'').trim(); } }
  _fxpSt=o; _fxpStV=L10N.ver; return o; }
function fxpName(n){ n=String(n==null?'':n); if(!L10N.dat||!n) return n;
  const one=w=>{ const v=tl(w); if(v!=null&&v!==w) return v; return fxpStatusNames()[w]||w; }, ps=n.split(/\s+and\s+/).map(one);
  if(ps.length===1) return ps[0]; try{ return new Intl.ListFormat(L10N.code,{type:'conjunction'}).format(ps); }catch(e){ return ps.reduce((x,y)=>txp('fxp_and','{v1} and {v2}',x,y)); } }
function fxpOn(e,main,dur){ let low=false; const parts=String(e).split(/\s+and\s+/).map((p,i)=>{ p=p.trim(); let m; const first=main&&i===0;
    if(m=p.match(/^-(\d+)% (Attack|Defense)$/)){ const r=first?txp('fxp_t_lower',"Lowers the target's {v1} by {v2}%",FXP_STAT(m[2]),m[1]):(low?txp('fxp_on_lower_also','its {v1} by {v2}%',FXP_STAT(m[2]),m[1]):txp('fxp_on_lower','lowering its {v1} by {v2}%',FXP_STAT(m[2]),m[1])); low=true; return r; }
    low=false;
    if(m=p.match(/^-(\d+) Speed stages?$/)) return first?txp('fxp_t_spd','Gives the target a -{v1} Speed debuff',m[1]):txp('fxp_on_spd','giving it a -{v1} Speed debuff',m[1]);
    if(m=p.match(/^bleeds (\d+)% max HP\/turn$/)) return first?txp('fxp_t_bleed','Makes the target bleed {v1}% of its max HP each turn',m[1]):txp('fxp_on_bleed','making it bleed {v1}% of its max HP each turn',m[1]);
    if(m=p.match(/^(?:takes )?(\d+)% max HP\/turn$/)) return first?txp('fxp_t_dot','Costs the target {v1}% of its max HP each turn',m[1]):txp('fxp_on_dot','costing it {v1}% of its max HP each turn',m[1]);
    if(m=p.match(/^-(\d+)% damage$/)) return first?txp('fxp_t_lower_dmg',"Lowers the target's damage by {v1}%",m[1]):txp('fxp_on_lower_dmg','lowering its damage by {v1}%',m[1]);
    if(m=p.match(/^takes \+(\d+)% damage from all sources$/)) return first?txp('fxp_t_take_all','Makes the target take {v1}% more damage from all sources',m[1]):txp('fxp_on_take_all','making it take {v1}% more damage from all sources',m[1]);
    if(m=p.match(/^takes \+(\d+)% damage from the user$/)) return first?txp('fxp_t_take_user','Makes the target take {v1}% more damage from the user',m[1]):txp('fxp_on_take_user','making it take {v1}% more damage from the user',m[1]);
    if(m=p.match(/^takes \+(\d+)% damage from the next hit against it$/)) return first?txp('fxp_t_take_next','Makes the target take {v1}% more damage from the next hit',m[1]):txp('fxp_on_take_next','making it take {v1}% more damage from the next hit',m[1]);
    if(m=p.match(/^'s healing received -(\d+)%$/)) return first?txp('fxp_t_heal_cut','Cuts the healing the target receives by {v1}%',m[1]):txp('fxp_on_heal_cut','cutting the healing it receives by {v1}%',m[1]);
    return null; });
  if(parts.indexOf(null)>=0) return null; let out=parts[0]; for(let i=1;i<parts.length;i++) out=txp('fxp_and','{v1} and {v2}',out,parts[i]);
  return main?(dur?txp('fxp_t_for','{v1} for {v2}.',out,dur):txp('fxp_t_end','{v1}.',out)):out; }
function fxpCond2(c){ return fxpKinIn(c).replace(/\bon target\b/,()=>tx('fxp_on_the_target','on the target')).replace(/\bon self\b/,()=>tx('fxp_on_the_user','on the user'))
  .replace(/^if user's\b/,()=>tx('fxp_if_users',"if the user's")).replace(/^if user\b/,()=>tx('fxp_if_user','if the user')); }
function fxpCond(c){ let m; c=String(c);
  if(m=c.match(/^per (.+?) \(max \+(\d+)%\)$/)) return txp('fxp_c_per_max','for each {v1}, up to {v2}% more',fxpCond2(m[1]),m[2]);
  if(m=c.match(/^per (.+)$/)) return txp('fxp_c_per','for each {v1}',fxpCond2(m[1]));
  if(/^if user has an active Defense buff\s+—\s+consumes it$/.test(c)) return tx('fxp_c_def_consume','if the user has an active Defense buff, and uses that buff up');
  return fxpTail(fxpCond2(c)); }
const FXP_RULES=[
  [/^Damage only$/, ()=>tx('fxp_dmg','Deals damage.')],
  [/^Damage$/, ()=>tx('fxp_dmg','Deals damage.')],
  [/^Damage as (\d+) hits$/, m=>txp('fxp_dmg_hits','Deals damage in {v1} hits.',m[1])],
  [/^Damage as (\d+) rapid hits$/, m=>txp('fxp_dmg_rapid','Deals damage in {v1} rapid hits.',m[1])],
  [/^Damage as (\d+) hits, one per head$/, m=>txp('fxp_dmg_heads','Deals damage in {v1} hits, one per head.',m[1])],
  [/^\+(\d+)% more (.+)$/, m=>txp('fxp_more','Deals {v1}% more damage {v2}.',m[1],fxpCond(m[2]))],
  [/^each \+(\d+)% more (.+)$/, m=>txp('fxp_each_more','Each hit deals {v1}% more damage {v2}.',m[1],fxpCond(m[2]))],
  [/^second hit \+(\d+)% more (.+)$/, m=>txp('fxp_second_more','The second hit deals {v1}% more damage {v2}.',m[1],fxpCond(m[2]))],
  [/^ignores (\d+)% of target Defense$/, m=>txp('fxp_ignore_def',"Ignores {v1}% of the target's Defense.",m[1])],
  [/^\+(\d+)% damage vs (.+) targets$/, m=>txp('fxp_vs_type','Deals {v1}% more damage against {v2} targets.',m[1],fxpName(m[2]))],
  [/^user heals (\d+)% of damage dealt$/, m=>txp('fxp_lifesteal','The user heals for {v1}% of the damage dealt.',m[1])],
  [/^user loses (\d+)% max HP$/, m=>txp('fxp_recoil','The user loses {v1}% of its max HP.',m[1])],
  [/^heal self (\d+)% max HP$/, m=>txp('fxp_heal_self','The user heals {v1}% of its max HP.',m[1])],
  [/^user drains the amount siphoned$/, ()=>tx('fxp_drain','The user heals by the amount drained.')],
  [/^Heal one ally (\d+)% max HP$/, m=>txp('fxp_heal_ally','Heals one ally for {v1}% of its max HP.',m[1])],
  [/^\+(\d+)% (Attack|Defense) \(self, (\d+)t\) per debuff cleansed$/, m=>txp('fxp_self_per_cleanse',"Raises the user's {v1} by {v2}% for each debuff removed, for {v3}.",FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^\+(\d+)% (Attack|Defense) \(self, (\d+)t\) if a debuff was cleansed$/, m=>txp('fxp_self_if_cleanse',"Raises the user's {v1} by {v2}% for {v3} if a debuff was removed.",FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^\+(\d+)% (Attack|Defense) \(self, (\d+)t\)$/, m=>txp('fxp_self_stat',"Raises the user's {v1} by {v2}% for {v3}.",FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^(?:Self |self |user )?\+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_self_stat',"Raises the user's {v1} by {v2}% for {v3}.",FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^\+(\d+)% Attack next turn$/, m=>txp('fxp_self_atk_next',"Raises the user's Attack by {v1}% next turn.",m[1])],
  [/^(?:Self |self )?\+(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_self_spd','Gives the user a {v1} for {v2}.',FXP_SPD('+',m[1]),FXP_N(m[2]))],
  [/^self -(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_self_spd','Gives the user a {v1} for {v2}.',FXP_SPD('-',m[1]),FXP_N(m[2]))],
  [/^(?:One|one) ally \+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_ally_stat',"Raises one ally's {v1} by {v2}% for {v3}.",FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^All allies \+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_team_stat',"Raises all allies' {v1} by {v2}% for {v3}.",FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^One ally \+(\d+)% Attack and \+(\d+)% Defense, (\d+)t$/, m=>txp('fxp_ally_atkdef',"Raises one ally's Attack by {v1}% and Defense by {v2}% for {v3}.",m[1],m[2],FXP_N(m[3]))],
  [/^All allies \+(\d+)% Attack and \+(\d+)% Defense, (\d+)t$/, m=>txp('fxp_team_atkdef',"Raises all allies' Attack by {v1}% and Defense by {v2}% for {v3}.",m[1],m[2],FXP_N(m[3]))],
  [/^One ally \+(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_ally_spd','Gives one ally a {v1} for {v2}.',FXP_SPD('+',m[1]),FXP_N(m[2]))],
  [/^All allies \+(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_team_spd','Gives all allies a {v1} for {v2}.',FXP_SPD('+',m[1]),FXP_N(m[2]))],
  [/^One ally takes -(\d+)% damage, (\d+)t$/, m=>txp('fxp_ally_dr','One ally takes {v1}% less damage for {v2}.',m[1],FXP_N(m[2]))],
  [/^All allies take -(\d+)% damage, (\d+)t$/, m=>txp('fxp_team_dr','All allies take {v1}% less damage for {v2}.',m[1],FXP_N(m[2]))],
  [/^(.+) allies take -(\d+)% damage instead$/, m=>txp('fxp_kin_dr','{v1} allies take {v2}% less damage instead.',fxpName(m[1]),m[2])],
  [/^[Nn]ext hit taken -(\d+)%$/, m=>txp('fxp_shield1','The user takes {v1}% less damage from the next hit.',m[1])],
  [/^Next (\d+) hits taken -(\d+)%$/, m=>txp('fxp_shieldn','The user takes {v2}% less damage from the next {v1} hits.',m[1],m[2])],
  [/^One ally's next hit taken -(\d+)%$/, m=>txp('fxp_ally_shield1','One ally takes {v1}% less damage from the next hit.',m[1])],
  [/^[Cc]leanse 1 (?:self )?debuff$/, ()=>tx('fxp_cleanse1','Removes 1 debuff from the user.')],
  [/^[Cc]leanse 1 self debuff \(no transfer to target\)$/, ()=>tx('fxp_cleanse1_keep','Removes 1 debuff from the user without passing it on to the target.')],
  [/^[Cc]leanse up to (\d+) (?:self )?debuffs$/, m=>txp('fxp_cleanse_upto','Removes up to {v1} debuffs from the user.',m[1])],
  [/^[Cc]leanse all (?:self )?debuffs$/, ()=>tx('fxp_cleanse_all','Removes all debuffs from the user.')],
  [/^all allies cleanse 1 debuff$/, ()=>tx('fxp_team_cleanse1','Removes 1 debuff from every ally.')],
  [/^One ally cleanses 1 debuff$/, ()=>tx('fxp_ally_cleanse1','Removes 1 debuff from one ally.')],
  [/^One ally cleanses up to (\d+) debuffs$/, m=>txp('fxp_ally_cleanse_upto','Removes up to {v1} debuffs from one ally.',m[1])],
  [/^One ally cleanses all debuffs$/, ()=>tx('fxp_ally_cleanse_all','Removes all debuffs from one ally.')],
  [/^One ally cleanses 1 debuff and gains \+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_ally_cleanse1_stat','Removes 1 debuff from one ally and raises its {v1} by {v2}% for {v3}.',FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^Transfer 1 debuff from self to the target$/, ()=>tx('fxp_transfer1','Moves 1 debuff from the user to the target.')],
  [/^Transfer up to (\d+) self debuffs to the target$/, m=>txp('fxp_transfer_upto',"Moves up to {v1} of the user's debuffs to the target.",m[1])],
  [/^Transfer all self debuffs to the target$/, ()=>tx('fxp_transfer_all',"Moves all of the user's debuffs to the target.")],
  [/^Remove 1 buff from the target$/, ()=>tx('fxp_strip1','Removes 1 buff from the target.')],
  [/^Remove up to (\d+) buffs from the target$/, m=>txp('fxp_strip_upto','Removes up to {v1} buffs from the target.',m[1])],
  [/^Remove all buffs from the target$/, ()=>tx('fxp_strip_all','Removes all buffs from the target.')],
  [/^Steal 1 buff from the target$/, ()=>tx('fxp_steal1','Steals 1 buff from the target.')],
  [/^Copy the target's newest buff to self$/, ()=>tx('fxp_copy',"Copies the target's newest buff to the user.")],
  [/^cannot be cleansed$/, ()=>tx('fxp_no_cleanse','It cannot be removed.')],
  [/^consumes the mark$/, ()=>tx('fxp_consume_mark','Uses up the mark.')],
  [/^Duration doubled vs (.+) targets$/, m=>txp('fxp_dur_double','Lasts twice as long against {v1} targets.',fxpName(m[1]))],
  [/^each applies (\d+)t of (.+)$/, m=>txp('fxp_each_apply','Each hit applies {v1} for {v2}.',fxpName(m[2]),FXP_N(m[1]))],
  [/^each applies ([^:]+): (\d+)% max HP\/turn, (\d+)t$/, m=>txp('fxp_each_apply_dot','Each hit applies {v1} for {v2}, costing the target {v3}% of its max HP each turn.',fxpName(m[1]),FXP_N(m[3]),m[2])],
  [/^applies ([^:]+): (\d+)% max HP\/turn, (\d+)t$/, m=>txp('fxp_apply_dot','Applies {v1} for {v2}, costing the target {v3}% of its max HP each turn.',fxpName(m[1]),FXP_N(m[3]),m[2])],
  [/^[Tt]he next creature to hit the user gains ([^:]+): (?:target )?(.+), (\d+)t$/, m=>{ const on=fxpOn(m[2]); return on?txp('fxp_retal_status','The next creature to hit the user gets {v1} for {v2}, {v3}.',fxpName(m[1]),FXP_N(m[3]),on):null; }],
  [/^attackers take ([^:]+): (\d+)% max HP over (\d+)t$/, m=>txp('fxp_attackers_dot','Attackers get {v1}, losing {v2}% of their max HP over {v3}.',fxpName(m[1]),m[2],FXP_N(m[3]))],
  [/^attackers take (\d+)% of their damage back$/, m=>txp('fxp_thorns','Attackers take {v1}% of their damage back.',m[1])],
  [/^Once per battle: the first killing blow this battle leaves the user at (\d+) HP instead$/, m=>txp('fxp_survive','Once per battle, the first killing blow leaves the user at {v1} HP instead.',m[1])],
  [/^Once per battle: survive with (\d+) HP, then user -(\d+)% Defense, (\d+)t$/, m=>txp('fxp_survive_def','Once per battle, the user survives a killing blow with {v1} HP, then its Defense drops by {v2}% for {v3}.',m[1],m[2],FXP_N(m[3]))],
  [/^if target already has (.+), extend it (\d+)t$/, m=>txp('fxp_extend','If the target already has {v1}, it lasts {v2} longer.',fxpName(m[1]),FXP_N(m[2]))],
  [/^if target has (.+), also -(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_if_has_lower','If the target has {v1}, its {v2} also drops by {v3}% for {v4}.',fxpName(m[1]),FXP_STAT(m[3]),m[2],FXP_N(m[4]))],
  [/^if no (.+) ally, self \+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_if_no_kin',"With no {v1} ally, raises the user's {v2} by {v3}% for {v4} instead.",fxpName(m[1]),FXP_STAT(m[3]),m[2],FXP_N(m[4]))],
  [/^if the user was not hit last turn, also \+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_if_unhit','If the user was not hit last turn, also raises its {v1} by {v2}% for {v3}.',FXP_STAT(m[2]),m[1],FXP_N(m[3]))],
  [/^user's next attack deals \+(\d+)% more$/, m=>txp('fxp_next_atk',"The user's next attack deals {v1}% more damage.",m[1])],
  [/^([^:]+): (?:user deals )?\+(\d+)% more to the target, (\d+)t$/, m=>txp('fxp_mark_user','Applies {v1} for {v2}, so the user deals {v3}% more damage to the target.',fxpName(m[1]),FXP_N(m[3]),m[2])],
  [/^([^:]+): \+(\d+)% damage from all sources, (\d+)t$/, m=>txp('fxp_mark_all','Applies {v1} for {v2}, making the target take {v3}% more damage from all sources.',fxpName(m[1]),FXP_N(m[3]),m[2])],
  [/^([^:]+): \+(\d+)% damage from the user, (\d+)t$/, m=>txp('fxp_mark_from_user','Applies {v1} for {v2}, making the target take {v3}% more damage from the user.',fxpName(m[1]),FXP_N(m[3]),m[2])],
  [/^([^:]+): \+(\d+)% damage from the next hit against it$/, m=>txp('fxp_mark_next','Applies {v1}, making the target take {v2}% more damage from the next hit.',fxpName(m[1]),m[2])],
  [/^([^:]+): the next hit against the target deals \+(\d+)% more$/, m=>txp('fxp_charged','Applies {v1}, so the next hit against the target deals {v2}% more damage.',fxpName(m[1]),m[2])],
  [/^([^:]+): the target's next attack deals -(\d+)% damage$/, m=>txp('fxp_foreseen',"Applies {v1}, so the target's next attack deals {v2}% less damage.",fxpName(m[1]),m[2])],
  [/^([^:]+): (\d+)%\/turn, (\d+)t$/, m=>txp('fxp_apply_dot','Applies {v1} for {v2}, costing the target {v3}% of its max HP each turn.',fxpName(m[1]),FXP_N(m[3]),m[2])],
  [/^([^:]+): (\d+)t$/, m=>txp('fxp_apply_dur','Applies {v1} for {v2}.',fxpName(m[1]),FXP_N(m[2]))],
    [/^(?:([^:]+): )?target('s healing received -\d+%|\s.+?)(?:, (\d+)t)?(?:, (stacks up to (\d+) times|does not stack))?$/, m=>{ const on=fxpOn(m[2].replace(/^\s+/,'')); if(!on) return null;
     const st=m[4]?(' '+(m[5]?txp('fxp_stacks','Stacks up to {v1} times.',m[5]):tx('fxp_no_stack','Does not stack.'))):'';
     if(m[1]) return (m[3]?txp('fxp_apply_on_dur','Applies {v1} to the target for {v2}, {v3}.',fxpName(m[1]),FXP_N(m[3]),on):txp('fxp_apply_on','Applies {v1} to the target, {v2}.',fxpName(m[1]),on))+st;
     const v=fxpOn(m[2].replace(/^\s+/,''),true,m[3]?FXP_N(m[3]):''); return v?v+st:null; }],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) ally (?:gains |gain )?\+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_kin1_stat','{v1} ally gains {v2}% {v3} for {v4}.',fxpName(m[1]),m[2],FXP_STAT(m[3]),FXP_N(m[4]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies (?:gain )?\+(\d+)% (Attack|Defense), (\d+)t$/, m=>txp('fxp_kin_stat','{v1} allies gain {v2}% {v3} for {v4}.',fxpName(m[1]),m[2],FXP_STAT(m[3]),FXP_N(m[4]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies gain \+(\d+)% (Attack|Defense), (\d+)t when this hits$/, m=>txp('fxp_kin_stat_hit','{v1} allies gain {v2}% {v3} for {v4} when this hits.',fxpName(m[1]),m[2],FXP_STAT(m[3]),FXP_N(m[4]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies (?:gain |get )\+(\d+)% (Attack|Defense) instead$/, m=>txp('fxp_kin_stat_instead','{v1} allies gain {v2}% {v3} instead.',fxpName(m[1]),m[2],FXP_STAT(m[3]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies also gain \+(\d+)% (Attack|Defense)$/, m=>txp('fxp_kin_stat_also','{v1} allies also gain {v2}% {v3}.',fxpName(m[1]),m[2],FXP_STAT(m[3]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies gain \+(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_kin_spd','{v1} allies gain a {v2} for {v3}.',fxpName(m[1]),FXP_SPD('+',m[2]),FXP_N(m[3]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies also gain \+(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_kin_spd_also','{v1} allies also gain a {v2} for {v3}.',fxpName(m[1]),FXP_SPD('+',m[2]),FXP_N(m[3]))],
  [/^((?:[A-Z][a-z]+ and )?[A-Z][a-z]+) allies gain \+(\d+) Speed stages? for (\d+)t instead$/, m=>txp('fxp_kin_spd_instead','{v1} allies gain a {v2} for {v3} instead.',fxpName(m[1]),FXP_SPD('+',m[2]),FXP_N(m[3]))],
  [/^([A-Z][\w'-]* targets) also take -(\d+) Speed stages?, (\d+)t$/, m=>txp('fxp_targets_also_spd','{v1} also get a {v2} for {v3}.',L10N.dat?fxpName(m[1].replace(/ targets$/,'')):m[1],FXP_SPD('-',m[2]),FXP_N(m[3]))],
  [/^(.+?) allies: (.+)$/, m=>txp('fxp_with_kin','With {v1} allies, {v2}',fxpName(m[1]),fxpClause(m[2]).replace(/^The /,()=>{ const t=String(tx('fxp_the_lc','the')).trim(); return /[A-Za-z\u00C0-\u024F]$/.test(t)?t+' ':t; }))],
  [/^\(This move IS the synergy: (.+)\.\)$/, m=>txp('fxp_own_synergy','This move is its own synergy: {v1}.',fxpTail(m[1]))]
];
function fxpClause(c){ c=String(c||'').trim().replace(/\.$/,''); if(!c) return '';
  for(let i=0;i<FXP_RULES.length;i++){ const m=c.match(FXP_RULES[i][0]); if(m){ const v=FXP_RULES[i][1](m,c); if(v) return v; } }
  const t=fxpTail(c); return t.charAt(0).toUpperCase()+t.slice(1)+(/[.!?]$/.test(t)?'':'.'); }
function fxProse(raw){ const s=String(raw==null?'':raw).trim(); if(!s||s==='-') return s;
  const cl=s.replace(/\.$/,'').split(/\s*;\s*(?![^()]*\))/).filter(Boolean); let m;
    if(cl.length>1&&cl[0]==='Damage'){ const j=cl.findIndex(c=>/^\+\d+% more /.test(c));
    if(j>0){ const r=cl.splice(j,1)[0]; cl.splice(0,1,r); }
    else if(m=cl[1].match(/^ignores (\d+)% of target Defense$/)){ cl.splice(0,2); return [txp('fxp_dmg_ignore',"Deals damage that ignores {v1}% of the target's Defense.",m[1])].concat(cl.map(fxpClause)).filter(Boolean).join(' '); } }
  return cl.map(fxpClause).filter(Boolean).join(' '); }
window.fxProse=fxProse;
})();
