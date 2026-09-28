/* cry_bank.js - HERUMON TOWER CREATURE CRIES (#993 paragraph 4, D 2026-09-25).

   "When a monster is selected for battle on the floor, it always plays the same high pitch screech sound.
   Go look at all the old gen pokemon sounds and plan to create a sound for each of our creatures that will
   play when they are engaged and when they advance. No high pitched annoying screeches. Creature sounds along
   the same line should be similar, the higher stages become more menacing or more complex."

   HOW THE OLD GENERATIONS DID IT. A gen-1 cry is not a recording: it is a short program for the Game Boy's
   two pulse channels and its noise channel, and there are only ~38 of those programs (the "base cries").
   Every species is a base cry plus two numbers - a pitch shift and a tempo/length change - so an evolution
   line usually shares ONE base and the later stage plays it lower and longer (gen 2 added bases and kept the
   scheme). That is the model here, one level richer because we are not bound to three channels:

     line  -> a KIND (the base cry: grunt, caw, croak, hiss, moan, clang ... chosen from the line's body and
              type by tools/gen_cries.py and written into LINES below), MODS from its secondary type, a pitch
              offset from its size, and a seed. Every stage of a line shares all four.
     stage -> the menace ladder: each stage is ~3.5 semitones lower (stage 3 a fifth under stage 1), longer,
              with more partials, more roughness, a sub-octave and one more syllable at stage 3.

   NO SCREECH, BY CONSTRUCTION. The tone is additive: a partial is only summed if it sits under 3.6 kHz, noise
   bands top out at 3.4 kHz, and the finished cry goes through a 4th-order low-pass at 3.8 kHz. tools/
   probe_993_cries.py measures every one of the 300 and fails any with more than 1% of its energy above 4 kHz.

   ONE CEILING. Each cry is normalised to the house ceiling the bank uses (-18 LUFS integrated, ITU-R BS.1770-4,
   K-weighted at 48 kHz; peak never above -1 dBFS), then played at CRY_GAIN on the sfx bus, like any cue.

   Pure functions over numbers: the same file renders in the client (window.CRY_BANK, played through
   AFX_BANK.pcm), on the codex site's creature page, and in node for the probe. Deterministic: the same
   creature renders the same samples everywhere. */
(function(root){
'use strict';
const SR=48000;
const CAP_HZ=3600;          // no partial is summed above this
const LP_HZ=3800;           // final 4th-order low-pass
const NORM_LUFS=-18, NORM_PEAK=-1;
const CRY_GAIN=0.5;         // on the sfx bus: the evolve cue's own gain, so a cry sits with the cues, not over them

/* THE BASE CRIES. f0 Hz at stage 1 before the line offset; harm = partial count; tilt = 1/k^tilt roll-off;
   duty = pulse-wave weighting (gen-1's duty cycle - 0.5 is hollow/square, 0.125 thin/nasal); F = two formant
   centres (Hz) and bw their width; vib [Hz, semitones]; jit = pitch random walk (st); am [Hz, depth] =
   roughness/buzz/gurgle; noise = breath/rasp level, band [lo,hi]; clicks /s; syl syllables of ms with gap ms;
   cont = pitch contour [start, 35%, end] in semitones; atk ms. */
const KINDS={
  grunt:  {f0:120,harm:22,tilt:1.0,duty:0.35,F:[600,1150],bw:260,vib:[5,0.1],jit:0.25,am:[26,0.25],noise:0.20,band:[300,1400],clicks:0,syl:2,ms:170,gap:55,cont:[2,3,-3],atk:12},
  howl:   {f0:260,harm:14,tilt:1.2,duty:0.5, F:[520,1000],bw:300,vib:[5.5,0.35],jit:0.05,am:[0,0],noise:0.06,band:[400,1600],clicks:0,syl:1,ms:520,gap:0,cont:[-5,2,-4],atk:60},
  yowl:   {f0:300,harm:14,tilt:1.1,duty:0.4, F:[700,1400],bw:320,vib:[6,0.3],jit:0.1,am:[0,0],noise:0.05,band:[500,1800],clicks:0,syl:1,ms:420,gap:0,cont:[-3,3,-6],atk:40},
  bellow: {f0:110,harm:24,tilt:0.95,duty:0.45,F:[480,900],bw:240,vib:[4,0.15],jit:0.12,am:[18,0.15],noise:0.10,band:[200,1100],clicks:0,syl:1,ms:520,gap:0,cont:[0,2,-4],atk:45},
  caw:    {f0:420,harm:8,tilt:1.1,duty:0.3, F:[900,1700],bw:380,vib:[0,0],jit:0.15,am:[40,0.25],noise:0.12,band:[700,2400],clicks:0,syl:2,ms:150,gap:70,cont:[1,2,-3],atk:10},
  chirp:  {f0:520,harm:6,tilt:1.4,duty:0.5, F:[1100,2000],bw:500,vib:[9,0.25],jit:0.0,am:[0,0],noise:0.02,band:[900,2600],clicks:0,syl:3,ms:95,gap:45,cont:[-4,2,4],atk:6},
  croak:  {f0:95,harm:26,tilt:0.85,duty:0.25,F:[420,1100],bw:220,vib:[0,0],jit:0.1,am:[22,0.45],noise:0.08,band:[250,1200],clicks:0,syl:2,ms:190,gap:70,cont:[0,1,-2],atk:8},
  bubble: {f0:210,harm:6,tilt:1.6,duty:0.5, F:[350,800],bw:260,vib:[8,0.8],jit:0.0,am:[11,0.45],noise:0.05,band:[250,900],clicks:2,syl:3,ms:120,gap:50,cont:[-5,4,-1],atk:10},
  click:  {f0:170,harm:10,tilt:1.1,duty:0.2, F:[800,1600],bw:400,vib:[0,0],jit:0.2,am:[0,0],noise:0.22,band:[900,2600],clicks:14,syl:2,ms:160,gap:60,cont:[0,1,-1],atk:4},
  song:   {f0:140,harm:12,tilt:1.3,duty:0.5, F:[380,760],bw:220,vib:[4,0.4],jit:0.0,am:[0,0],noise:0.04,band:[200,900],clicks:0,syl:1,ms:760,gap:0,cont:[-4,5,-2],atk:120},
  rumble: {f0:78,harm:30,tilt:0.9,duty:0.45,F:[380,780],bw:200,vib:[3,0.1],jit:0.1,am:[14,0.35],noise:0.14,band:[120,800],clicks:0,syl:1,ms:560,gap:0,cont:[1,0,-3],atk:70},
  chitter:{f0:260,harm:10,tilt:1.1,duty:0.25,F:[1000,1900],bw:420,vib:[0,0],jit:0.3,am:[34,0.5],noise:0.14,band:[900,2800],clicks:8,syl:4,ms:75,gap:35,cont:[2,0,-2],atk:5},
  buzz:   {f0:150,harm:16,tilt:0.95,duty:0.2,F:[700,1500],bw:380,vib:[0,0],jit:0.05,am:[95,0.6],noise:0.08,band:[500,2000],clicks:0,syl:1,ms:420,gap:0,cont:[-2,1,-1],atk:25},
  hiss:   {f0:130,harm:8,tilt:1.3,duty:0.5, F:[500,1000],bw:300,vib:[0,0],jit:0.05,am:[0,0],noise:0.62,band:[1100,2500],clicks:0,syl:1,ms:520,gap:0,cont:[0,0,-3],atk:35,tone:0.35},
  roar:   {f0:100,harm:30,tilt:0.8,duty:0.4, F:[560,1100],bw:280,vib:[4.5,0.15],jit:0.3,am:[30,0.3],noise:0.22,band:[200,1400],clicks:0,syl:1,ms:620,gap:0,cont:[-2,3,-5],atk:55},
  moan:   {f0:150,harm:10,tilt:1.35,duty:0.5,F:[380,820],bw:220,vib:[3.5,0.35],jit:0.15,am:[0,0],noise:0.22,band:[250,1200],clicks:0,syl:1,ms:720,gap:0,cont:[2,0,-6],atk:140},
  wail:   {f0:230,harm:8,tilt:1.45,duty:0.5, F:[420,900],bw:260,vib:[5,0.45],jit:0.05,am:[0,0],noise:0.28,band:[400,1600],clicks:0,syl:1,ms:640,gap:0,cont:[-4,3,-3],atk:110},
  clang:  {f0:140,harm:12,tilt:0.9,duty:0.5, F:[700,1500],bw:500,vib:[0,0],jit:0.0,am:[7,0.2],noise:0.06,band:[600,2400],clicks:0,syl:2,ms:210,gap:60,cont:[0,0,-1],atk:4,inh:0.035},
  drone:  {f0:90,harm:18,tilt:1.0,duty:0.5, F:[400,900],bw:300,vib:[0,0],jit:0.0,am:[5,0.3],noise:0.06,band:[150,900],clicks:0,syl:1,ms:680,gap:0,cont:[0,1,-2],atk:160,inh:0.012},
  puff:   {f0:140,harm:6,tilt:1.6,duty:0.5, F:[400,900],bw:300,vib:[0,0],jit:0.0,am:[0,0],noise:0.55,band:[300,1500],clicks:0,syl:3,ms:110,gap:60,cont:[2,0,-2],atk:6,tone:0.4},
  creak:  {f0:85,harm:24,tilt:0.9,duty:0.15,F:[500,1200],bw:260,vib:[0,0],jit:0.9,am:[16,0.5],noise:0.12,band:[300,1500],clicks:6,syl:1,ms:520,gap:0,cont:[3,0,-2],atk:30},
  gurgle: {f0:120,harm:14,tilt:1.1,duty:0.4, F:[380,850],bw:220,vib:[6,0.5],jit:0.2,am:[9,0.55],noise:0.12,band:[200,1000],clicks:3,syl:2,ms:230,gap:50,cont:[-2,2,-3],atk:15},
  chime:  {f0:330,harm:6,tilt:1.5,duty:0.5, F:[700,1500],bw:600,vib:[5,0.15],jit:0.0,am:[0,0],noise:0.02,band:[600,2000],clicks:0,syl:3,ms:150,gap:40,cont:[0,0,0],atk:5,inh:0.02,steps:[0,4,7,12]},
  choir:  {f0:200,harm:10,tilt:1.3,duty:0.5, F:[520,1000],bw:260,vib:[5,0.2],jit:0.0,am:[0,0],noise:0.05,band:[300,1400],clicks:0,syl:1,ms:780,gap:0,cont:[-2,0,0],atk:180,fifth:0.5},
  purr:   {f0:110,harm:18,tilt:1.0,duty:0.3, F:[450,950],bw:220,vib:[0,0],jit:0.05,am:[24,0.7],noise:0.10,band:[200,900],clicks:0,syl:1,ms:420,gap:0,cont:[0,1,-2],atk:40}
};
/* A PRIMARY TYPE'S DEFAULT KIND, used when gen_cries.py found no body word. */
const TYPE_KIND={Beast:'grunt',Avian:'caw',Aquatic:'bubble',Insect:'buzz',Spectral:'wail',Arthropod:'click',Amphibian:'croak',
  Construct:'clang',Serpent:'hiss',Flora:'creak',Mollusk:'gurgle',Dragon:'roar',Fungal:'puff',Vampiric:'hiss',Undead:'moan',
  Reptile:'hiss',Elemental:'drone',Ooze:'gurgle',Fey:'chime',Void:'drone',Chimera:'roar',Celestial:'choir'};
/* SECONDARY TYPE MODS: small deltas layered on the base so a Beast·Undead and a plain Beast share a kind and
   still differ the way their design does. chorus = a detuned double; ring = an inharmonic partial set at sqrt 2;
   crackle = sparse impulses; swell = a long attack. */
const MODS={
  Elemental:{chorus:0.006,crackle:30},
  Fey:{bell:0.30,vibD:0.15},
  Undead:{noise:0.12,jit:0.2,contEnd:-2},
  Eldritch:{ring:0.35,vibD:0.2},
  Construct:{inh:0.02,duty:0.5},
  Horror:{amD:0.25,amR:33,sub:0.25},
  Parasite:{clicks:6,jit:0.2},
  Void:{swell:1,sub:0.35,ring:0.2},
  Flora:{jit:0.4,clicks:3},
  Beast:{noise:0.08,amD:0.1},
  Arthropod:{clicks:6},
  Spectral:{noise:0.12,vibD:0.2},
  Aquatic:{vibD:0.3,amD:0.12,amR:9},
  Fungal:{noise:0.1},
  Demon:{sub:0.35,amD:0.2,amR:28},
  Aberration:{jump:1,jit:0.3},
  Avian:{contEnd:3},
  Dragon:{sub:0.25,noise:0.06},
  Amphibian:{amD:0.2,amR:20},
  Celestial:{fifth:0.35},
  Serpent:{hissAdd:0.25},
  Reptile:{hissAdd:0.15},
  Insect:{amD:0.2,amR:80},
  Vampiric:{hissAdd:0.2,contEnd:-2},
  Mollusk:{amD:0.2,amR:10},
  Ooze:{amD:0.25,amR:8},
  Chimera:{chorus:0.012,sub:0.2}
};
/* ===== LINES: generated by tools/gen_cries.py from codex/creatures.csv - do not hand-edit between the markers.
   [kind, mods ('+'-joined secondary/tertiary types), size offset in semitones (the line's body word:
   tiny/young + , colossal/titanic -), design word the kind was chosen from ('' = the primary type's default)]. */
/* @@LINES@@ */
const LINES={
  THORNBACK:["grunt", "", 0, "boar"],
  DUSTHOUND:["howl", "", 0, "canine"],
  BARROWMOLE:["grunt", "", 0, "mole"],
  BRAMBLEFAWN:["bellow", "Flora", 0, "fawn"],
  NIGHTMARE:["moan", "Fey+Spectral", 0, "phantom"],
  GOLGOTH:["grunt", "Elemental", -3, ""],
  WYCHROOT:["creak", "", 0, "tree"],
  GARROTE:["moan", "Construct", 0, "revenant"],
  GALLOWSBIRD:["caw", "Undead", 0, "carrion"],
  HERNE:["bellow", "Beast", -3, "stag"],
  TIDECRAWLER:["click", "Arthropod", 0, "barnacle"],
  SALTJAW:["bubble", "", 0, "fish"],
  BRINEFROG:["croak", "", 0, "toad"],
  CRESTMANTIS:["chitter", "Arthropod", 0, "mantis"],
  DUSKSCALE:["hiss", "", -3, "monitor"],
  RUSALKA:["moan", "Fey", 0, "drowned"],
  BULWARK:["gurgle", "", 0, "snail"],
  NETHEREEL:["bubble", "Void", 0, "eel"],
  CORALHYDRA:["hiss", "", 0, "serpent"],
  DAGON:["moan", "Undead", -3, "drowned"],
  SANDSKITTER:["moan", "Undead", 3, "ghost"],
  DUNECOIL:["hiss", "Elemental", 3, "serpent"],
  FATA:["yowl", "Spectral+Fey", 0, "cat"],
  SIMOOM:["clang", "Elemental", 0, "construct"],
  ECHIDNA:["hiss", "", -3, "serpent"],
  VOIDSIPHON:["gurgle", "", 3, "squid"],
  EMBERCLAW:["hiss", "Elemental", 0, "iguana"],
  ZARATAN:["rumble", "Construct", -3, "tortoise"],
  MARID:["drone", "Fey", 0, "storm"],
  OUROBOROS:["hiss", "Eldritch", 0, "serpent"],
  GLOOMGRUB:["chitter", "", 3, "larva"],
  THORNHUSK:["chitter", "Flora", 0, "beetle"],
  SPOREFLY:["buzz", "Fungal", 0, "fly"],
  ARACHNE:["chitter", "Horror", 0, "spider"],
  CARNIFORA:["creak", "Parasite", 0, "plant"],
  PLAGUECARRIER:["chitter", "Parasite", 3, "beetle"],
  DEVOUT:["chitter", "Fey", 0, "mantis"],
  LOCUST:["buzz", "", 0, "swarm"],
  VESPERA:["buzz", "Fungal", 0, "wasp"],
  YGGDRASIL:["creak", "Eldritch", 0, "root"],
  CLIFFPINCER:["click", "", 0, "crab"],
  CRUSHMAUL:["chitter", "", 0, "pillbug"],
  SLAGWORM:["gurgle", "Reptile", 0, "slug"],
  RIDGEDRAKE:["roar", "Reptile", 0, "drake"],
  STONECALLER:["click", "Construct", 0, "lobster"],
  SANGLEECH:["gurgle", "Parasite", -3, "leech"],
  CRAGGERNAUT:["click", "Construct", -3, "crustacean"],
  VOIDSHELL:["chitter", "Void", 0, "scorpion"],
  TALOS:["rumble", "Construct", -3, "colossus"],
  MAGMACRAWLER:["clang", "Elemental", 0, "obsidian"],
  GUSTWING:["chirp", "", 3, "chick"],
  STORMCROW:["caw", "Elemental", 0, "crow"],
  THUNDERMOTH:["buzz", "Elemental", -3, "moth"],
  ROC:["caw", "", -3, "eagle"],
  GALEHOWL:["howl", "Fey+Beast", 0, "wolf"],
  VOLTMANTLE:["caw", "Elemental+Aquatic", 0, ""],
  COUATL:["chirp", "Avian+Dragon", 0, "feather"],
  TYPHON:["roar", "Elemental", 0, "dragon"],
  ANZU:["caw", "Eldritch", 0, "storm-bird"],
  STORMFATHER:["roar", "Elemental", 0, "dragon"],
  BOGHOPPER:["croak", "", 0, "toad"],
  MIRENEWT:["croak", "", 0, "newt"],
  ROTFLY:["buzz", "Undead", 0, "fly"],
  LICHFROG:["croak", "Undead", 0, "frog"],
  WISPMAW:["croak", "Fey+Amphibian", 0, "toad"],
  GRENDEL:["croak", "", -3, "salamander"],
  DRAUGR:["moan", "Fey", 0, "ghost"],
  GALLOWVINE:["creak", "Parasite", 0, "vine"],
  MIREMOTHER:["croak", "Horror", -3, "frog"],
  CENOTAPH:["moan", "Eldritch", 0, "absence"],
  GLOOMCAP:["puff", "", 0, "mushroom"],
  INKMANTLE:["gurgle", "", 0, "octopus"],
  VEINMOLD:["puff", "Parasite+Construct", 0, "fung"],
  SIBYL:["gurgle", "Spectral", 0, "nautilus"],
  VERTIGO:["click", "Aberration", 0, "crustacean"],
  LAMPYRE:["drone", "Fey+Beast", 3, ""],
  SPOREWHALE:["song", "Aquatic", 0, "whale"],
  RIFTANGLER:["bubble", "Void", 0, "angler"],
  MYCELIUM:["puff", "Eldritch", 0, "spore"],
  KRAKEN:["bubble", "Eldritch", -3, ""],
  CRYSTALWRAITH:["moan", "", 0, "phantom"],
  ASHBAT:["chitter", "Undead", 0, "bat"],
  GEMBORN:["clang", "Construct", 0, "gem"],
  BLOODCARVER:["hiss", "Beast", 0, ""],
  SHATTERSPECTER:["moan", "Horror", 0, "ghost"],
  VOIDHOUND:["hiss", "Void", 0, ""],
  DOPPELGANGER:["wail", "Fey", 0, "reflection"],
  NOSFERATU:["hiss", "Horror", -3, "vampir"],
  PHYLACTERY:["moan", "Undead", 0, "undead sorcerer"],
  SPECULUM:["wail", "Horror", 0, "reflection"],
  CINDERSHARD:["clang", "Elemental", 0, "obsidian"],
  ASHWALKER:["rumble", "Undead", 0, "golem"],
  MOLOCH:["clang", "Elemental", 0, "iron"],
  BLAZEWYRM:["hiss", "Elemental", 0, "serpent"],
  INFERNOCHIMERA:["roar", "Elemental", 0, "chimera"],
  FERRODRAKE:["roar", "Dragon", -3, "dragon"],
  IGNIFER:["roar", "Elemental", 0, "dragon"],
  VIGIL:["clang", "Eldritch", 0, "built"],
  PYRIEL:["drone", "Demon", 0, "principle"],
  DEMIURGE:["drone", "Eldritch", 0, "designed"]
};
/* @@END@@ */

// ---- deterministic randomness -----------------------------------------------------------------------------
const fnv=s=>{ let h=2166136261>>>0; s=String(s); for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619)>>>0; } return h>>>0; };
const rng=seed=>{ let a=seed>>>0; return ()=>{ a=(a+0x6D2B79F5)>>>0; let t=a; t=Math.imul(t^(t>>>15),t|1); t^=t+Math.imul(t^(t>>>7),t|61); return ((t^(t>>>14))>>>0)/4294967296; }; };

/* spec(lineId, stage, t1, t2, t3) -> the full parameter set for one creature. The LINE decides kind, mods,
   offset and seed; the STAGE applies the menace ladder. t1..t3 (its types) are only read when the line is not
   in LINES (a line added to the codex after the table was generated still gets a cry). */
const spec=(lineId,stage,t1,t2,t3)=>{
  const L=LINES[String(lineId||'').toUpperCase()]||[TYPE_KIND[t1]||'grunt',[t2,t3].filter(Boolean).join('+'),0,''];
  const K=KINDS[L[0]]||KINDS.grunt; const s=Math.max(0,Math.min(2,(+stage||1)-1));
  const seed=fnv('cry:'+String(lineId||t1||'?').toUpperCase()); const R=rng(seed);
  const P=Object.assign({tone:1,inh:0,sub:0,chorus:0,fifth:0,ring:0,bell:0,crackle:0,swell:0,jump:0,hissAdd:0,steps:null},K);
  P.F=K.F.slice(); P.band=K.band.slice(); P.cont=K.cont.slice(); P.vib=K.vib.slice(); P.am=K.am.slice();
  // the line's own variation, shared by every stage: a detune, a contour lean, a syllable rhythm
  const lean=(R()-0.5)*3, detune=(R()-0.5)*3, rhythm=[0,1,2,3,4].map(()=>0.8+R()*0.4), sylSt=[0,1,2,3,4].map(()=>Math.round((R()-0.5)*6));
  String(L[1]||'').split('+').filter(Boolean).forEach(m=>{ const M=MODS[m]; if(!M) return;
    if(M.chorus) P.chorus=Math.max(P.chorus,M.chorus); if(M.crackle) P.crackle+=M.crackle; if(M.bell) P.bell+=M.bell;
    if(M.vibD){ P.vib[1]+=M.vibD; if(!P.vib[0]) P.vib[0]=5; } if(M.noise) P.noise+=M.noise; if(M.jit) P.jit+=M.jit;
    if(M.contEnd) P.cont[2]+=M.contEnd; if(M.ring) P.ring+=M.ring; if(M.inh) P.inh+=M.inh; if(M.duty) P.duty=M.duty;
    if(M.amD){ P.am[1]=Math.min(0.8,P.am[1]+M.amD); if(!P.am[0]) P.am[0]=M.amR||20; } if(M.sub) P.sub+=M.sub;
    if(M.clicks) P.clicks+=M.clicks; if(M.swell) P.swell=1; if(M.jump) P.jump=1; if(M.fifth) P.fifth+=M.fifth; if(M.hissAdd) P.hissAdd+=M.hissAdd; });
  // THE MENACE LADDER: lower, longer, richer, rougher, a sub-octave, and one more syllable at the top
  P.f0=K.f0*Math.pow(2,((+L[2]||0)+detune-3.5*s)/12);
  P.F=P.F.map(f=>f*Math.pow(2,(-1.5*s)/12));
  P.harm=K.harm+4*s; P.tilt=Math.max(0.6,K.tilt-0.12*s);
  P.ms=K.ms*(1+0.22*s); P.gap=K.gap*(1+0.1*s); P.syl=K.syl+((s===2&&K.syl>1)?1:0); // a one-breath kind (howl, moan, choir) grows longer, not doubled
  P.am=[P.am[0]||(s?24:0), Math.min(0.8,P.am[1]+0.1*s)]; if(!P.am[1]) P.am[0]=0;
  P.sub+=(s===0?0:0.15*s); P.noise+=0.05*s; P.jit+=0.08*s;
  P.cont=P.cont.map((c,i)=>(c+(i===1?lean:0))*(1+0.2*s));
  P.stage=s+1; P.kind=L[0]; P.mods=L[1]||''; P.word=L[3]||''; P.seed=seed; P.rhythm=rhythm; P.sylSt=sylSt;
  P.line=String(lineId||'').toUpperCase();
  return P; };

// ---- the renderer ---------------------------------------------------------------------------------------
const TAU=Math.PI*2;
const biquad=(type,f,q)=>{ const w=TAU*f/SR, c=Math.cos(w), a=Math.sin(w)/(2*q); let b0,b1,b2;
  if(type==='lp'){ b0=(1-c)/2; b1=1-c; b2=(1-c)/2; } else if(type==='hp'){ b0=(1+c)/2; b1=-(1+c); b2=(1+c)/2; } else { b0=a; b1=0; b2=-a; }
  const a0=1+a; return {b0:b0/a0,b1:b1/a0,b2:b2/a0,a1:-2*c/a0,a2:(1-a)/a0,x1:0,x2:0,y1:0,y2:0}; };
const run=(F,x)=>{ const y=F.b0*x+F.b1*F.x1+F.b2*F.x2-F.a1*F.y1-F.a2*F.y2; F.x2=F.x1; F.x1=x; F.y2=F.y1; F.y1=y; return y; };
const envAt=(u,atkU)=>{ if(u<atkU) return u/atkU; const r=0.62; if(u<r) return 1-0.25*(u-atkU)/Math.max(1e-6,r-atkU);
  return 0.75*0.5*(1+Math.cos(Math.PI*(u-r)/(1-r))); };

/* render(P) -> Float32Array at 48 kHz, normalised to the ceiling. */
const render=P=>{
  const R=rng(P.seed^(P.stage*0x9E3779B1));
  const syls=[]; let t=0;
  for(let i=0;i<P.syl;i++){ const d=P.ms*P.rhythm[i%5]*(i===P.syl-1&&P.syl>1?1.25:1); syls.push({t0:t,d:d,st:(P.steps?P.steps[i%P.steps.length]:(i?P.sylSt[i%5]:0))}); t+=d+P.gap; }
  const total=Math.ceil((t-P.gap+40)*SR/1000); const out=new Float32Array(total);
  const bp=biquad('bp',Math.sqrt(P.band[0]*P.band[1]),Math.max(0.5,Math.sqrt(P.band[0]*P.band[1])/(P.band[1]-P.band[0])));
  const hs=biquad('bp',1800,1.2);
  const ck=biquad('bp',1500,2.5);
  let ph=0, ph2=0, ph3=0, jit=0, clickE=0, crE=0; const pw=Math.max(0.3,P.tone==null?1:P.tone);
  const amps=new Float64Array(64), ratio=new Float64Array(64); let nk=0;
  const weights=f=>{ nk=0; let e=0; for(let k=1;k<=P.harm&&k<64;k++){ const r=Math.pow(k,1+P.inh); if(r*f>CAP_HZ) break;
      const fk=r*f; let a=Math.pow(k,-P.tilt)*Math.max(0.05,Math.abs(Math.sin(Math.PI*k*P.duty)));
      a*=0.35+Math.exp(-Math.pow((fk-P.F[0])/P.bw,2))+0.7*Math.exp(-Math.pow((fk-P.F[1])/(P.bw*1.3),2));
      amps[k]=a; ratio[k]=r; e+=a*a; nk=k; }
    const n=1/Math.sqrt(e||1); for(let k=1;k<=nk;k++) amps[k]*=n; };
  let si=0;
  for(let n=0;n<total;n++){ const ms=n*1000/SR;
    while(si<syls.length-1&&ms>=syls[si].t0+syls[si].d) si++;
    const S=syls[si]; const u=(ms-S.t0)/S.d; if(u<0||u>1){ out[n]=0; continue; }
    const atkU=Math.min(0.6,(P.swell?0.45*S.d:P.atk)/S.d);
    let env=envAt(u,atkU);
    if(P.am[1]) env*=1-P.am[1]*(0.5-0.5*Math.cos(TAU*P.am[0]*ms/1000));
    // contour: quadratic through start / 35% / end, plus the syllable step, vibrato and a random walk
    const c=P.cont; let st=(u<0.35)?(c[0]+(c[1]-c[0])*(u/0.35)):(c[1]+(c[2]-c[1])*((u-0.35)/0.65));
    st+=S.st+P.vib[1]*Math.sin(TAU*P.vib[0]*ms/1000);
    if((n&127)===0){ jit+=(R()-0.5)*P.jit; jit*=0.92; if(P.jump&&R()<0.004) jit+=(R()<0.5?-4:4); }
    st+=jit;
    const f=P.f0*Math.pow(2,st/12);
    if((n&63)===0) weights(f);
    ph+=TAU*f/SR; if(ph>TAU*4096) ph-=TAU*4096;
    let tone=0; for(let k=1;k<=nk;k++) tone+=amps[k]*Math.sin(ph*ratio[k]);
    if(P.sub) tone+=P.sub*0.8*Math.sin(ph*0.5);
    if(P.chorus){ ph2+=TAU*f*(1+P.chorus)/SR; tone+=0.45*(Math.sin(ph2)+0.5*Math.sin(2*ph2)+0.25*Math.sin(3*ph2)); }
    if(P.fifth){ ph3+=TAU*f*1.5/SR; if(1.5*f*3<CAP_HZ) tone+=P.fifth*(Math.sin(ph3)+0.4*Math.sin(2*ph3)+0.2*Math.sin(3*ph3)); }
    if(P.ring&&f*1.414<CAP_HZ) tone+=P.ring*Math.sin(ph*1.414)*Math.sin(ph*0.5);
    if(P.bell&&f*2.76<CAP_HZ) tone+=P.bell*Math.sin(ph*2.76)*Math.exp(-3*u);
    const wn=R()*2-1;
    let nz=run(bp,wn)*P.noise*3;
    if(P.hissAdd) nz+=run(hs,R()*2-1)*P.hissAdd*2.2;
    if(P.clicks&&R()<P.clicks/SR) clickE=1; if(clickE>0.001){ nz+=run(ck,wn)*clickE*3; clickE*=0.985; }
    if(P.crackle&&R()<P.crackle/SR) crE=1; if(crE>0.001){ nz+=wn*crE*0.5; crE*=0.93; }
    out[n]=env*(pw*tone*0.5+nz);
  }
  // THE CAP: high-pass 70 Hz, two 3.8 kHz low-pass stages (4th order), a 10 ms tail fade
  const h1=biquad('hp',70,0.707), l1=biquad('lp',LP_HZ,0.541), l2=biquad('lp',LP_HZ,1.307);
  for(let n=0;n<total;n++) out[n]=run(l2,run(l1,run(h1,out[n])));
  const fade=Math.round(0.01*SR); for(let i=0;i<fade;i++) out[total-1-i]*=i/fade;
  const m=measure(out); let g=Math.pow(10,(NORM_LUFS-m.lufs)/20); if(m.peak>0) g=Math.min(g,Math.pow(10,NORM_PEAK/20)/m.peak);
  for(let n=0;n<total;n++) out[n]*=g;
  return out; };

/* measure(x) -> {lufs, peak, seconds}. ITU-R BS.1770-4 integrated loudness at 48 kHz: K-weighting (the spec's
   coefficients - the ones tools/afx_measure.py uses), 400 ms blocks at 75% overlap, absolute gate -70, relative
   -10 LU; a clip shorter than one block is one block. The same arithmetic the bank was normalised with. */
const measure=x=>{ const S1={b0:1.53512485958697,b1:-2.69169618940638,b2:1.19839281085285,a1:-1.69065929318241,a2:0.73248077421585};
  const S2={b0:1.0,b1:-2.0,b2:1.0,a1:-1.99004745483398,a2:0.99007225036621};
  const k=new Float64Array(x.length); let a=Object.assign({x1:0,x2:0,y1:0,y2:0},S1), b=Object.assign({x1:0,x2:0,y1:0,y2:0},S2); let peak=0;
  for(let i=0;i<x.length;i++){ k[i]=run(b,run(a,x[i])); const v=Math.abs(x[i]); if(v>peak) peak=v; }
  const B=Math.round(0.4*SR), H=Math.round(0.1*SR); const z=[];
  if(x.length<=B){ let s=0; for(let i=0;i<x.length;i++) s+=k[i]*k[i]; z.push(s/B); }
  else for(let st=0;st+B<=x.length;st+=H){ let s=0; for(let i=st;i<st+B;i++) s+=k[i]*k[i]; z.push(s/B); }
  const L=v=>-0.691+10*Math.log10(Math.max(v,1e-12));
  let g=z.filter(v=>L(v)>-70); if(!g.length) return {lufs:-70,peak:peak,seconds:x.length/SR};
  const rel=L(g.reduce((p,v)=>p+v,0)/g.length)-10; g=g.filter(v=>L(v)>rel);
  return {lufs:L(g.reduce((p,v)=>p+v,0)/Math.max(1,g.length)), peak:peak, seconds:x.length/SR}; };

// ---- the cache and the public face ------------------------------------------------------------------------
const cache={};
/* samples(row) -> Float32Array for a creatures.csv row (ID, Line_ID, Stage, Type_*), rendered once. */
const keyOf=row=>row?(String(row.Line_ID||'').toUpperCase()+':'+(+row.Stage||1)):'';
const samples=row=>{ if(!row) return null; const k=keyOf(row); if(cache[k]) return cache[k];
  const P=spec(row.Line_ID,row.Stage,row.Type_Primary,row.Type_Secondary,row.Type_Tertiary); return (cache[k]=render(P)); };
/* describe(row) -> the one-line label the codex prints next to its play button. */
const describe=row=>{ if(!row) return ''; const P=spec(row.Line_ID,row.Stage,row.Type_Primary,row.Type_Secondary,row.Type_Tertiary);
  return P.kind+(P.mods?' · '+P.mods.toLowerCase().split('+').join(' · '):'')+' · stage '+P.stage; };
/* playOn(ctx, dest, row, gain) -> a stop function. The codex page's player (the client plays through
   AFX_BANK.pcm so the sliders and the mute apply). */
const playOn=(ctx,dest,row,gain)=>{ const x=samples(row); if(!ctx||!x) return ()=>{};
  const b=ctx.createBuffer(1,x.length,SR); if(b.copyToChannel) b.copyToChannel(x,0); else b.getChannelData(0).set(x);
  const s=ctx.createBufferSource(), g=ctx.createGain(); g.gain.value=(gain==null?CRY_GAIN:gain); s.buffer=b; s.connect(g); g.connect(dest||ctx.destination); s.start();
  return ()=>{ try{ s.stop(); }catch(e){} }; };
const API={ SR:SR, CAP_HZ:CAP_HZ, LP_HZ:LP_HZ, NORM:{lufs:NORM_LUFS,peak:NORM_PEAK}, GAIN:CRY_GAIN,
  KINDS:KINDS, MODS:MODS, TYPE_KIND:TYPE_KIND, LINES:LINES, spec:spec, render:render, measure:measure, samples:samples, keyOf:keyOf, describe:describe, playOn:playOn };
if(typeof module!=='undefined'&&module.exports) module.exports=API;
if(root) root.CRY_BANK=API;
})(typeof window!=='undefined'?window:(typeof globalThis!=='undefined'?globalThis:this));
