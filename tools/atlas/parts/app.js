
(function(){
"use strict";
const D = window.__DCDATA__;
const WORLD_TWH = 30900, WORLD_CO2_MT = 37800;

/* ---------- projection: Equal Earth (Šavrič, Patterson & Jenny 2018) ---------- */
const A1=1.340264,A2=-0.081106,A3=0.000893,A4=0.003796;
const XR=2.706615, YR=1.317446, S=1000/(2*XR);
function rawY(lat){
  const th=Math.asin(0.8660254037844386*Math.sin(lat*Math.PI/180));
  const t2=th*th, t6=t2*t2*t2, t8=t6*t2;
  return (YR-th*(A1+A2*t2+A3*t6+A4*t8))*S;
}
const LAT_TOP=84, LAT_BOT=-58, YOFF=rawY(LAT_TOP), H=rawY(LAT_BOT)-YOFF;
function proj(lon,lat){
  const l=lon*Math.PI/180, p=lat*Math.PI/180;
  const th=Math.asin(0.8660254037844386*Math.sin(p));
  const t2=th*th, t6=t2*t2*t2, t8=t6*t2;
  const x=2*Math.sqrt(3)*l*Math.cos(th)/(3*(9*A4*t8+7*A3*t6+3*A2*t2+A1));
  const y=th*(A1+A2*t2+A3*t6+A4*t8);
  return [(x+XR)*S,(YR-y)*S-YOFF];
}

/* ---------- marks ---------- */
let uid=0;
const marks = [];
D.sites.forEach(s=>{ s.id='s'+(uid++); s.kind='site'; marks.push(s); });
D.metros.forEach(m=>{ m.id='m'+(uid++); m.kind='metro'; m.o=null; marks.push(m); });
marks.forEach(m=>{ const p=proj(m.lon,m.lat); m.px=p[0]; m.py=p[1]; });

const iso2reg={};
D.regions.forEach(r=>r.iso.forEach(i=>iso2reg[i]=r));

/* ---------- state ---------- */
const st = {
  scenario:'now', sites:true, metros:true, grid:true,
  status:'all', op:'all', country:'all', q:'',
  kIea:0.398, kMetro:0.60, kNat:0.70, kAi:0.70, cut:0, grow:0.21, marg:true,
  sel:null, selRegion:null, tab:'data'
};

/* ---------- model ---------- */
function capOf(m){
  if(st.scenario==='all') return m.kind==='metro' ? m.mw+(m.pmw||0) : Math.max(m.mw, m.pmw||0);
  if(st.scenario==='2030') return m.pmw ? Math.max(m.mw,m.pmw) : m.mw;
  return m.mw;
}
function pipelineOf(m){
  return m.kind==='metro' ? (m.pmw||0) : Math.max(0,(m.pmw||0)-m.mw);
}
const kOf = m => m.b==='fac' ? st.kAi : st.kMetro;
function energyOf(m){ return capOf(m)*8760*kOf(m)/1e6; }
const ciOf = m => m.ci*(1-st.cut);
function twhOf(m,mw){ return mw*8760*kOf(m)/1e6; }
function newCi(iso, fallback){
  const n = st.marg && NEWLOAD[iso] ? NEWLOAD[iso].ci*(1-st.cut) : null;
  return n!=null ? n : fallback;
}
function blendCi(m){
  // US campuses carry their own AVERT marginal rate; everything else falls back to the country figure
  if(st.marg && m.nci) return m.nci*(1-st.cut);
  return newCi(m.c, ciOf(m));
}
function emitOf(m){
  const cap=capOf(m), base=Math.min(cap,m.mw), extra=Math.max(0,cap-m.mw);
  return (twhOf(m,base)*ciOf(m) + twhOf(m,extra)*blendCi(m))/1000;
}
let announcedGW=null;
function announcedUplift(){
  if(announcedGW===null) announcedGW = marks.reduce((a,m)=>a+pipelineOf(m),0)/1000;
  return announcedGW;
}
const OVR_REG={cn:'CHN'};
function regionStats(r){
  let gw = r.gw * (st.scenario==='2030' ? r.g : 1);
  if(st.scenario==='all'){
    const share = r.gw / D.regions.reduce((a,x)=>a+x.gw,0);
    gw = r.gw + announcedUplift()*share;
  }
  const ovKey=OVR_REG[r.k], ov=ovKey?OVR[ovKey]:null;
  let twh, baseTwh;
  if(ov){
    baseTwh = ov.twh;
    twh = st.scenario==='now' ? ov.twh
        : (st.scenario==='2030' ? (ov.twh2030||ov.twh) : ov.twh*(gw/r.gw));
  } else {
    twh = gw*1000*8760*st.kIea/1e6;
    baseTwh = Math.min(gw,r.gw)*1000*8760*st.kIea/1e6;
  }
  const extraTwh=Math.max(0,twh-baseTwh);
  const gci=r.ci*(1-st.cut);
  const solo = r.iso.length<=2 ? r.iso[0] : null;
  const bci = newCi(solo, gci);
  const mt = (Math.min(twh,baseTwh)*gci + extraTwh*bci)/1000;
  return {mw:gw*1000, twh, mt, ov:!!ov};
}
const NAT=D.nat||{}, NAMES=D.names||{}, COMPLETE=D.complete||{}, BENCH=D.bench||{}, MEAS=D.meas||{}, ANCH=D.anchors||[], DISP=D.disp||{}, OVR=D.ovr||{}, NEWLOAD=D.newload||{}
const POLICY=D.policy||{}, VINT=D.vint||null;
function countryMarks(iso){
  return marks.filter(m=> m.c===iso && (m.kind==='metro' || !m.inm));
}
function countryStats(iso){
  const rk=COMPLETE[iso];
  if(rk){
    const r=D.regions.find(x=>x.k===rk), s=regionStats(r);
    return {name:NAMES[iso]||iso, iso, mw:s.mw, twh:s.twh, mt:s.mt, basis:'complete', ci:r.ci*(1-st.cut), n:marks.filter(m=>m.c===iso).length};
  }
  const list=countryMarks(iso); let mw=0, metroMw=0;
  list.forEach(m=>{ mw+=capOf(m); if(m.kind==='metro') metroMw+=capOf(m); });
  // metro capacity -> whole-country consumption, calibrated on Ireland (CSO) and the Netherlands (CBS)
  const siteMw = mw-metroMw;
  const twh = (metroMw*st.kNat + siteMw*st.kAi)*8760/1e6;
  const ciRaw = (D.ci[iso]||0)*(1-st.cut);
  const base = (list.reduce((a,m)=>a+(m.kind==='metro'?m.mw*st.kNat:m.mw*st.kAi),0))*8760/1e6;
  const extra = Math.max(0, twh-base);
  const mt = (Math.min(twh,base)*ciRaw + extra*newCi(iso, ciRaw))/1000;
  return {name:NAMES[iso]||iso, iso, mw, twh, mt, basis:'scaled', ci:ciRaw, n:marks.filter(m=>m.c===iso).length};
}
function countriesWithData(){
  const seen={};
  marks.forEach(m=>{ seen[m.c]=(seen[m.c]||0)+m.mw; });
  return Object.keys(seen).filter(c=>NAT[c]).sort((a,b)=>seen[b]-seen[a]);
}
function worldStats(){
  let mw=0,twh=0,mt=0;
  D.regions.forEach(r=>{const s=regionStats(r); mw+=s.mw; twh+=s.twh; mt+=s.mt;});
  return {mw,twh,mt};
}

/* ---------- filtering ---------- */
function filtersOn(){ return st.status!=='all' || st.op!=='all' || st.q!=='' || !st.sites || !st.metros; }
function visible(){
  const q=st.q.toLowerCase();
  return marks.filter(m=>{
    if(m.kind==='site' && !st.sites) return false;
    if(m.kind==='metro' && !st.metros) return false;
    if(st.status!=='all'){
      const s = m.kind==='metro' ? 'operational' : m.st;
      if(s!==st.status) return false;
    }
    if(st.op!=='all' && (m.o||'—')!==st.op) return false;
    if(st.country!=='all' && m.c!==st.country) return false;
    if(q && !((m.n+' '+(m.o||'')+' '+(m.loc||'')+' '+m.c).toLowerCase().includes(q))) return false;
    return true;
  });
}

/* ---------- formatting ---------- */
const nf=(v,d)=>v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
function fmtP(v){ if(v>=1000) return nf(v,0); if(v>=100) return nf(v,0); if(v>=10) return nf(v,1); if(v>=1) return nf(v,2); return nf(v,3); }
function capPair(mw){ return mw>=1000 ? [nf(mw/1000,1),'GW'] : [nf(mw,0),'MW']; }
function pctWorld(twh){ const p=twh/WORLD_TWH*100; return p>=1?nf(p,1):(p>=0.1?nf(p,2):(p>=0.001?nf(p,3):'<0.001')); }

/* ---------- map render ---------- */
const svg=document.getElementById('map'), gW=document.getElementById('gWorld'), gM=document.getElementById('gMarks');
svg.setAttribute('viewBox','0 0 1000 '+H.toFixed(1));
svg.querySelector('rect').setAttribute('height',H.toFixed(1));
const NS='http://www.w3.org/2000/svg';
const BUCKETS=[80,180,300,420,550,700];
function bucket(ci){ if(ci==null) return null; let i=0; while(i<BUCKETS.length && ci>BUCKETS[i]) i++; return i+1; }
const countryEls=[];
D.geo.forEach(c=>{
  if(c.i==='ATA'||c.n==='Antarctica') return;
  let d='';
  c.r.forEach(r=>{
    let open=false, prevLon=null;
    for(let i=0;i<r.length;i+=2){
      const lon=r[i], lat=r[i+1];
      const brk = prevLon!==null && Math.abs(lon-prevLon)>180;
      prevLon=lon;
      if(lat>LAT_TOP+2||lat<LAT_BOT-6){ if(open){d+='Z';open=false;} continue; }
      const p=proj(lon,lat);
      if(brk && open){ d+='Z'; open=false; }
      d+=(open?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1);
      open=true;
    }
    if(open) d+='Z';
  });
  if(!d) return;
  const el=document.createElementNS(NS,'path');
  el.setAttribute('d',d);
  el.setAttribute('stroke','var(--landEdge)');
  el.setAttribute('stroke-width','0.5');
  el.setAttribute('vector-effect','non-scaling-stroke');
  el.style.cursor = iso2reg[c.i] ? 'pointer' : 'default';
  el.__c=c; gW.appendChild(el); countryEls.push(el);
});
function paintCountries(){
  countryEls.forEach(el=>{
    const b = st.grid ? bucket(el.__c.ci) : null;
    el.setAttribute('fill', b ? 'var(--q'+b+')' : 'var(--land)');
  });
}

let k=1,tx=0,ty=0;
function applyCam(){
  gW.setAttribute('transform','translate('+tx+' '+ty+') scale('+k+')');
  layoutMarks();
}
function clampCam(){
  const w=1000,h=H;
  tx=Math.min(0,Math.max((1-k)*w,tx));
  ty=Math.min(0,Math.max((1-k)*h,ty));
}
function zoomAt(mx,my,f){
  const nk=Math.min(14,Math.max(1,k*f));
  tx = mx-(mx-tx)*nk/k; ty = my-(my-ty)*nk/k; k=nk;
  clampCam(); applyCam();
}
function svgPt(e){
  const r=svg.getBoundingClientRect();
  return [ (e.clientX-r.left)/r.width*1000, (e.clientY-r.top)/r.height*H ];
}
svg.addEventListener('wheel',e=>{ e.preventDefault(); const p=svgPt(e); zoomAt(p[0],p[1], e.deltaY<0?1.18:1/1.18); },{passive:false});
let drag=null;
svg.addEventListener('pointerdown',e=>{ drag={x:e.clientX,y:e.clientY,tx,ty,moved:false}; svg.setPointerCapture(e.pointerId); svg.classList.add('dragging'); });
svg.addEventListener('pointermove',e=>{
  if(!drag) return;
  const r=svg.getBoundingClientRect(), sc=1000/r.width;
  const dx=(e.clientX-drag.x)*sc, dy=(e.clientY-drag.y)*sc;
  if(Math.abs(dx)+Math.abs(dy)>3) drag.moved=true;
  tx=drag.tx+dx; ty=drag.ty+dy; clampCam(); applyCam();
});
function endDrag(e){ if(drag) svg.classList.remove('dragging'); drag=null; }
svg.addEventListener('pointerup',endDrag); svg.addEventListener('pointercancel',endDrag);
document.getElementById('zIn').onclick=()=>zoomAt(500,H/2,1.5);
document.getElementById('zOut').onclick=()=>zoomAt(500,H/2,1/1.5);
document.getElementById('zRst').onclick=()=>{k=1;tx=0;ty=0;applyCam();};

const tip=document.getElementById('tip');
function showTip(html,cx,cy){
  tip.innerHTML=html; tip.classList.add('on');
  const box=svg.getBoundingClientRect();
  const x=cx/1000*box.width, y=cy/H*box.height;
  tip.style.left=Math.min(Math.max(8,x+14), box.width-tip.offsetWidth-8)+'px';
  tip.style.top=Math.max(8, y-tip.offsetHeight-12)+'px';
}
const hideTip=()=>tip.classList.remove('on');
svg.addEventListener('pointerleave',hideTip);

countryEls.forEach(el=>{
  el.addEventListener('pointerenter',e=>{
    if(drag) return;
    const c=el.__c, r=iso2reg[c.i];
    const p=svgPt(e);
    showTip('<div class="tn">'+c.n+'</div>'+
      (c.ci!=null?'<div class="tr"><span>grid intensity</span><b>'+c.ci+' g/kWh</b></div>':'')+
      (NAT[c.i]&&marks.some(m=>m.c===c.i)
        ? '<div class="tr"><span>mapped here</span><b>'+marks.filter(m=>m.c===c.i).length+' locations</b></div>'
        : (r?'<div class="tr"><span>IEA region</span><b>'+r.n+'</b></div>':'')), p[0], p[1]);
  });
  el.addEventListener('click',()=>{
    if(drag&&drag.moved) return;
    const iso=el.__c.i;
    if(iso && NAT[iso] && marks.some(m=>m.c===iso)){ selectCountry(iso); return; }
    const r=iso2reg[iso]; if(r) selectRegion(r);
  });
});

/* markers */
let markEls=[];
function radius(mw){ return mw<=0 ? 3.4 : Math.max(2.6, 1.4+0.30*Math.sqrt(mw)); }
function renderMarks(){
  gM.textContent=''; markEls=[];
  const vis=visible().slice().sort((a,b)=>capOf(b)-capOf(a));
  vis.forEach(m=>{
    const c=document.createElementNS(NS,'circle');
    const site=m.kind==='site';
    const col = !site ? 'var(--ink2)' : (m.st==='operational' ? 'var(--s1)' : 'var(--s3)');
    c.setAttribute('r', radius(capOf(m)));
    c.setAttribute('fill', site?col:'none');
    c.setAttribute('fill-opacity', site?'0.92':'1');
    c.setAttribute('stroke', site?'var(--surface)':col);
    c.setAttribute('stroke-width', site?1.2:1.4);
    c.style.cursor='pointer';
    c.__m=m; gM.appendChild(c); markEls.push(c);
    c.addEventListener('pointerenter',()=>{
      if(drag&&drag.moved) return;
      const cap=capPair(capOf(m));
      showTip('<div class="tn">'+m.n+'</div>'+
        '<div class="tr"><span>'+(site?(m.o||'operator n/a'):'metro market')+'</span><b>'+(capOf(m)>0?cap[0]+' '+cap[1]:'not yet energized')+'</b></div>'+
        '<div class="tr"><span>electricity</span><b>'+fmtP(energyOf(m))+' TWh/yr</b></div>'+
        '<div class="tr"><span>emissions</span><b>'+fmtP(emitOf(m))+' Mt/yr</b></div>', m.sx, m.sy);
    });
    c.addEventListener('click',ev=>{ ev.stopPropagation(); if(drag&&drag.moved) return; selectMark(m); });
  });
  layoutMarks(); markSelection();
}
function layoutMarks(){
  markEls.forEach(c=>{ const m=c.__m; m.sx=m.px*k+tx; m.sy=m.py*k+ty; c.setAttribute('cx',m.sx); c.setAttribute('cy',m.sy); });
}
function markSelection(){
  markEls.forEach(c=>{
    const on = st.sel && c.__m.id===st.sel.id;
    c.setAttribute('stroke-width', on?3:(c.__m.kind==='site'?1.2:1.4));
    c.setAttribute('stroke', on?'var(--ink)':(c.__m.kind==='site'?'var(--surface)':'var(--ink2)'));
    if(on) c.parentNode.appendChild(c);
  });
}

/* ---------- scope + panels ---------- */
function selectMark(m){ st.sel=m; st.selRegion=null; render(); }
function selectRegion(r){ st.selRegion=r; st.sel=null; st.country='all'; document.getElementById('fCountry').value='all'; render(); }
function fitTo(iso){
  const f=D.geo.find(c=>c.i===iso); if(!f) return;
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  f.r.forEach(r=>{ for(let i=0;i<r.length;i+=2){ const p=proj(r[i],r[i+1]);
    if(p[0]<x0)x0=p[0]; if(p[0]>x1)x1=p[0]; if(p[1]<y0)y0=p[1]; if(p[1]>y1)y1=p[1]; } });
  marks.filter(m=>m.c===iso).forEach(m=>{ x0=Math.min(x0,m.px); x1=Math.max(x1,m.px); y0=Math.min(y0,m.py); y1=Math.max(y1,m.py); });
  const w=Math.max(24,x1-x0), h=Math.max(14,y1-y0), pad=1.45;
  k=Math.max(1,Math.min(9, Math.min(1000/(w*pad), H/(h*pad))));
  tx=500-((x0+x1)/2)*k; ty=H/2-((y0+y1)/2)*k;
  clampCam(); applyCam();
}
function selectCountry(iso){ st.country=iso; st.sel=null; st.selRegion=null; document.getElementById('fCountry').value=iso; fitTo(iso); render(); }
function clearScope(){ st.sel=null; st.selRegion=null; st.country='all'; document.getElementById('fCountry').value='all'; k=1;tx=0;ty=0; applyCam(); render(); }
document.getElementById('resetScope').onclick=clearScope;

function scopeStats(){
  if(st.sel){ const m=st.sel; return {name:m.n, iso:m.c, mw:capOf(m), twh:energyOf(m), mt:emitOf(m), kind:'mark'}; }
  if(st.country!=='all'){ const c=countryStats(st.country); return {name:c.name, iso:c.iso, mw:c.mw, twh:c.twh, mt:c.mt, kind:'country', basis:c.basis}; }
  if(st.selRegion){ const r=st.selRegion, s=regionStats(r);
    return {name:r.n, iso:(r.iso.length===1?r.iso[0]:null), mw:s.mw, twh:s.twh, mt:s.mt, kind:'region'}; }
  if(filtersOn()){
    const v=visible(); let mw=0,twh=0,mt=0;
    v.forEach(m=>{mw+=capOf(m); twh+=energyOf(m); mt+=emitOf(m);});
    return {name:v.length+' mapped locations', iso:null, mw,twh,mt,kind:'filter'};
  }
  const w=worldStats();
  return {name:'The world', iso:'WLD', mw:w.mw, twh:w.twh, mt:w.mt, kind:'world'};
}

function renderTiles(){
  const s=scopeStats();
  document.getElementById('scopeName').textContent=s.name;
  document.getElementById('resetScope').hidden = (s.kind==='world');
  const cp=capPair(s.mw);
  document.getElementById('tCap').innerHTML=cp[0]+'<small>'+cp[1]+'</small>';
  document.getElementById('tCapSub').textContent = st.scenario==='2030' ? 'IEA base case, 2030' : (st.scenario==='all' ? 'installed + everything announced' : 'energized today');
  document.getElementById('tTwh').innerHTML=fmtP(s.twh)+'<small>TWh / yr</small>';
  document.getElementById('tMt').innerHTML=fmtP(s.mt)+'<small>Mt / yr</small>';
  const rawNat = s.iso && NAT[s.iso] ? NAT[s.iso] : null;
  const grown = st.scenario!=='now' ? 1+st.grow : 1;
  const nat = rawNat ? [rawNat[0]*grown, rawNat[1], rawNat[2], rawNat[3]] : null;
  const label = s.iso==='WLD' ? 'the world' : (NAMES[s.iso]||'this country');
  const shareK=document.querySelector('#tShare').closest('.tile').querySelector('.k');
  if(nat){
    const pe=s.twh/nat[0]*100, pc=s.mt/nat[1]*100;
    shareK.textContent = s.iso==='WLD' ? 'Share of world electricity' : 'Share of national electricity';
    document.getElementById('tShare').innerHTML=(pe>=1?nf(pe,1):(pe>=0.1?nf(pe,2):nf(pe,3)))+'<small>%</small>';
    document.getElementById('tShareSub').textContent='of '+nf(nat[0],0)+' TWh generated'+(s.iso==='WLD'?' worldwide':' in '+label)+
      (st.scenario!=='now' ? ' · grid grown '+Math.round(st.grow*100)+'%' : ' · '+rawNat[2]);
    document.getElementById('tMtSub').textContent=(pc>=0.1?nf(pc,1):nf(pc,2))+'% of all CO₂ emitted '+(s.iso==='WLD'?'worldwide':'in '+label)+' ('+rawNat[3]+')'+(st.marg?' · new load at margin':'');
  }else{
    shareK.textContent='Share of world electricity';
    document.getElementById('tShare').innerHTML=pctWorld(s.twh)+'<small>%</small>';
    document.getElementById('tShareSub').textContent='of '+nf(NAT.WLD?NAT.WLD[0]:30900,0)+' TWh generated worldwide';
    document.getElementById('tMtSub').textContent = st.cut>0 ? 'grid '+Math.round(st.cut*100)+'% cleaner than today' : 'at today’s local grid mix';
  }

}

function listForCharts(){
  const anyLayer = st.sites||st.metros;
  if(anyLayer){
    return visible().map(m=>({key:m.id, n:m.n, sub:(m.kind==='site'?(m.o||'—'):'metro market'), mw:capOf(m), pipe:pipelineOf(m), twh:energyOf(m), mt:emitOf(m), ci:Math.round(ciOf(m)), yr:m.yr||'—', src:m.src, ref:m}))
      .sort((a,b)=>b.mt-a.mt);
  }
  return D.regions.map(r=>{const s=regionStats(r); return {key:r.k, n:r.n, sub:'IEA region', mw:s.mw, pipe:0, twh:s.twh, mt:s.mt, ci:Math.round(r.ci*(1-st.cut)), yr:'2024', src:'IEA Energy & AI Observatory', reg:r};})
    .sort((a,b)=>b.mt-a.mt);
}

/* ---------- wiring ---------- */

/* ---------- source registry ---------- */
const SRC = {
  epoch:{n:'Epoch AI — Frontier Data Centers',u:'https://epoch.ai/data/ai-data-centers',w:'Campus power capacity, from satellite imagery, permits and disclosures'},
  kf:{n:'Knight Frank — Data Centre Atlas 2026',u:'https://www.knightfrank.co.uk/site-assets/research/report-pdfs/data-centres/data-centre-atlas-2026.pdf',w:'Metro live IT capacity and announced pipeline'},
  cbre:{n:'CBRE — Global Data Center Trends 2026',u:'https://www.cbre.com/insights/reports/global-data-center-trends-2026',w:'Metro inventory, Latin America and US primary markets'},
  cbrena:{n:'CBRE — North America Data Center Trends',u:'https://www.cbre.com/insights/books/north-america-data-center-trends-h1-2026',w:'US market inventory'},
  cw:{n:'Cushman & Wakefield — Global Comparison 2023',u:'https://www.visualcapitalist.com/cp/top-data-center-markets/',w:'Colocation capacity — superseded where a 2026 figure exists'},
  iea:{n:'IEA — Energy and AI',u:'https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai',w:'Installed capacity and electricity demand by region'},
  owidci:{n:'Our World in Data — carbon intensity',u:'https://ourworldindata.org/grapher/carbon-intensity-electricity',w:'Lifecycle gCO₂ per kWh by country'},
  owidgen:{n:'Our World in Data — electricity generation',u:'https://ourworldindata.org/grapher/electricity-generation',w:'National generation, the denominator for share'},
  owidco2:{n:'Our World in Data — annual CO₂',u:'https://ourworldindata.org/grapher/annual-co2-emissions-per-country',w:'National total CO₂, the denominator for share'},
  egrid:{n:'EPA — eGRID2023',u:'https://www.epa.gov/egrid',w:'US subregion grid emission rates'},
  avert:{n:'EPA — AVERT v4.3 avoided emission rates',u:'https://www.epa.gov/avert/avoided-emission-rates-generated-avert',w:'US regional marginal emission rates, 2023 — what ramps to serve new load'},
  lbnl:{n:'Berkeley Lab — US Data Center Energy Usage',u:'https://newscenter.lbl.gov/2025/01/15/berkeley-lab-report-evaluates-increase-in-electricity-demand-from-data-centers/',w:'Measured US consumption, 176 TWh in 2023'},
  cso:{n:'CSO Ireland — Data Centres Metered Electricity',u:'https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/',w:'Measured Irish consumption, 7.66 TWh in 2025'},
  cbs:{n:'CBS Netherlands — data centre electricity',u:'https://www.cbs.nl/en-gb/news/2025/51/data-centres-consume-4-6-percent-of-the-netherlands-electricity',w:'Measured Dutch consumption, 5.10 TWh in 2024'},
};
function srcKeyFor(s){
  if(!s) return null;
  if(/Epoch/i.test(s)) return 'epoch';
  if(/Knight Frank/i.test(s)) return 'kf';
  if(/CBRE North|North America/i.test(s)) return 'cbrena';
  if(/CBRE/i.test(s)) return 'cbre';
  if(/Cushman/i.test(s)) return 'cw';
  return null;
}
const item=(k,meta,body,stale)=>{const s=SRC[k]; if(!s) return '';
  return '<a class="item'+(stale?' stale':'')+'" href="'+s.u+'" target="_blank" rel="noopener">'+
    '<span class="itemHead">'+s.n+'</span>'+
    (body?'<span class="itemBody">'+body+'</span>':'<span class="itemBody">'+s.w+'</span>')+
    (meta?'<span class="itemMeta">'+meta+'</span>':'')+'</a>';};

/* ---------- rail tabs ---------- */
const REGS=D.regs||[];
function regsFor(){
  if(st.sel){ const m=st.sel;
    return REGS.filter(r=> (m.kind==='site' && r.sites.indexOf(m.n)>=0) || (m.kind==='metro' && r.metros.indexOf(m.n)>=0)); }
  if(st.country!=='all') return REGS.filter(r=>r.iso===st.country);
  if(st.selRegion) return REGS.filter(r=>st.selRegion.iso.indexOf(r.iso)>=0);
  return REGS;
}
function tabData(){
  if(st.sel){
    const m=st.sel, site=m.kind==='site', cp=capPair(capOf(m));
    let planned='';
    if(m.pmw) planned='<div class="kv"><span>'+(site?'Announced end state':'Announced pipeline')+'</span><b>'+capPair(site?m.pmw:m.mw+m.pmw).join(' ')+(m.py?' · '+m.py:'')+'</b></div>';
    return '<div class="detMeta">'+(site?(m.o||'operator not disclosed'):'All operators in this market')+(m.loc?' · '+m.loc:'')+'</div>'+
      '<div class="badge" style="color:'+(!site?'var(--ink2)':(m.st==='operational'?'var(--s1)':'var(--s3)'))+'"><i class="dot"></i>'+
      (!site?'Metro market':(m.st==='operational'?'Drawing power':'Announced / building'))+'</div>'+
      '<div class="kv"><span>'+(site?'Facility power':'Live IT capacity')+'</span><b>'+(capOf(m)>0?cp.join(' '):'not yet energized')+'</b></div>'+
      planned+
      '<div class="kv"><span>Electricity</span><b>'+fmtP(energyOf(m))+' TWh/yr</b></div>'+
      '<div class="kv"><span>Grid intensity</span><b>'+Math.round(ciOf(m))+' g/kWh</b></div>'+
      '<div class="kv"><span>CO₂</span><b>'+fmtP(emitOf(m))+' Mt/yr</b></div>'+
      '<div class="kv"><span>Grid</span><b style="font-weight:500">'+m.cil+'</b></div>'+
      (m.av?'<div class="kv"><span>New load at margin</span><b>'+m.nci+' g/kWh</b></div>'+
            '<div class="kv"><span>AVERT region</span><b style="font-weight:500">'+m.av+
            (m.avc==='split'?' <span style="color:var(--s3)">· split state</span>':'')+'</b></div>':'')+
      (site&&m.inm?'<p class="note">Inside the '+m.inm+' market — already counted in that market\'s capacity, and not double-counted in country totals.</p>':'');
  }
  if(st.country!=='all'){
    const c=countryStats(st.country), rawN=NAT[st.country];
    const nat=rawN?[rawN[0]*(st.scenario!=='now'?1+st.grow:1), rawN[1]]:null;
    const list=countryMarks(st.country).sort((a,b)=>capOf(b)-capOf(a));
    const pe=nat?c.twh/nat[0]*100:null, pc=nat?c.mt/nat[1]*100:null;
    return '<div class="detMeta">'+list.length+' mapped location'+(list.length===1?'':'s')+
      (c.basis==='complete'?' · IEA national capacity':' · scaled from mapped metros')+'</div>'+
      '<div class="kv"><span>Capacity</span><b>'+capPair(c.mw).join(' ')+'</b></div>'+
      '<div class="kv"><span>Electricity</span><b>'+fmtP(c.twh)+' TWh/yr</b></div>'+
      (pe!=null?'<div class="kv"><span>of national electricity</span><b style="color:var(--s1)">'+(pe>=1?nf(pe,1):nf(pe,2))+'%</b></div>':'')+
      '<div class="kv"><span>Grid intensity</span><b>'+Math.round(c.ci)+' g/kWh</b></div>'+
      '<div class="kv"><span>CO₂</span><b>'+fmtP(c.mt)+' Mt/yr</b></div>'+
      (pc!=null?'<div class="kv"><span>of national CO₂</span><b style="color:var(--s1)">'+(pc>=0.1?nf(pc,1):nf(pc,2))+'%</b></div>':'')+
      (NEWLOAD[st.country]?(function(){const n=NEWLOAD[st.country];
        return '<div class="kv"><span>New load lands at</span><b style="color:'+(n.dir==='up'?'var(--s3)':'var(--s1)')+'">'+n.ci+' g/kWh</b></div>'+
          '<p class="note"><b>'+n.head+'</b> '+n.note+'</p>';})():'')+
      (OVR[st.country]?'<p class="note warn"><b>Counted on '+c.name+'&rsquo;s own national statistics</b> ('+fmtP(OVR[st.country].twh)+
          ' TWh, '+OVR[st.country].yr+'), not the IEA&rsquo;s '+fmtP(DISP[st.country]?DISP[st.country].vals[0].twh:0)+
          ' TWh. The two count different things — see Accuracy.</p>'
        :(DISP[st.country]?'<p class="note warn"><b>Disputed.</b> Published estimates span '+
          fmtP(DISP[st.country].vals[0].twh)+'–'+fmtP(DISP[st.country].vals[DISP[st.country].vals.length-1].twh)+' TWh.</p>':''))+
      '<p class="note'+(c.basis==='complete'?'':' warn')+'">'+(c.basis==='complete'
        ? 'Complete national capacity from the IEA; the energy factor is pinned by Berkeley Lab\'s measured US total.'
        : 'Estimated from mapped metro capacity using the ratio measured in Ireland and the Netherlands. Accurate where one metro is the whole national estate, a floor where it is not.')+'</p>';
  }
  if(st.selRegion){
    const r=st.selRegion, s=regionStats(r);
    const inReg=marks.filter(m=>r.iso.indexOf(m.c)>=0);
    return '<div class="detMeta">IEA region · '+r.iso.length+' countr'+(r.iso.length>1?'ies':'y')+'</div>'+
      '<div class="kv"><span>Capacity</span><b>'+capPair(s.mw).join(' ')+'</b></div>'+
      '<div class="kv"><span>Electricity</span><b>'+fmtP(s.twh)+' TWh/yr</b></div>'+
      '<div class="kv"><span>Grid intensity</span><b>'+Math.round(r.ci*(1-st.cut))+' g/kWh</b></div>'+
      '<div class="kv"><span>CO₂</span><b>'+fmtP(s.mt)+' Mt/yr</b></div>'+
      '<div class="kv"><span>Mapped here</span><b>'+inReg.length+' locations</b></div>';
  }
  const w=worldStats(), rows=D.regions.map(r=>({r,s:regionStats(r)})).sort((a,b)=>b.s.mt-a.s.mt).slice(0,6);
  const smw=D.sites.reduce((a,b)=>a+b.mw,0), mmw=D.metros.reduce((a,b)=>a+b.mw,0);
  const pipe=marks.reduce((a,m)=>a+pipelineOf(m),0)/1000;
  return '<div class="detMeta">Click any campus, market or country on the map.</div>'+
    '<div class="kv"><span>Capacity</span><b>'+capPair(w.mw).join(' ')+'</b></div>'+
    '<div class="kv"><span>Electricity</span><b>'+fmtP(w.twh)+' TWh/yr</b></div>'+
    '<div class="kv"><span>CO₂</span><b>'+fmtP(w.mt)+' Mt/yr</b></div>'+
    '<div class="kv"><span>Announced on top</span><b>'+nf(pipe,0)+' GW</b></div>'+
    '<div class="kv"><span>Mapped individually</span><b>'+D.metros.length+' markets · '+D.sites.length+' campuses</b></div>'+
    '<p class="note">'+nf(mmw/1000,1)+' GW of live market capacity and '+nf(smw/1000,1)+' GW of named campuses. Announced capacity of '+nf(pipe,0)+' GW added to today\'s fleet lands within 1% of the IEA\'s own 2030 base case.</p>'+
    '<p class="note warn"><b>China is counted on its own national statistics</b> (260 TWh, 2024) rather than the IEA\'s 100 TWh, which lifts the world total about 150 TWh above the IEA\'s published 415. Better evidenced for China, looser for cross-country comparison. See Accuracy.</p>';
}
function tabSrc(){
  let out='';
  if(st.sel){
    const m=st.sel, k=srcKeyFor(m.src), stale=!/2026/.test(m.yr||'');
    out+=item(k, 'figure dated '+(m.yr||'unknown')+(stale?' · superseded where newer data exists':''), null, stale);
    out+= m.c==='USA'&&m.kind==='site' ? item('egrid','subregion '+(m.cil||''),null) : item('owidci',null,null);
    if(m.av) out+=item('avert','AVERT region '+m.av+(m.avc==='split'?' · split state, assigned by eGRID subregion':''),null);
  } else if(st.country!=='all'){
    const c=countryStats(st.country);
    out += c.basis==='complete' ? item('iea','national installed capacity, 2024') : '';
    const ms=countryMarks(st.country).filter(m=>m.kind==='metro');
    const keys=[...new Set(ms.map(m=>srcKeyFor(m.src)).filter(Boolean))];
    keys.forEach(k=>{ const yrs=[...new Set(ms.filter(m=>srcKeyFor(m.src)===k).map(m=>m.yr))].join(', ');
      out+=item(k,'figures dated '+yrs, null, !/2026/.test(yrs)); });
    if(countryMarks(st.country).some(m=>m.kind==='site')) out+=item('epoch','campus power');
    out+=item('owidci'); out+=item('owidgen','latest year available'); out+=item('owidco2','latest year available');
    if(st.country==='USA') out+=item('avert','marginal rates for new load');
    if(MEAS[st.country]){ const kk={IRL:'cso',NLD:'cbs',USA:'lbnl'}[st.country]; if(kk) out+=item(kk,'independent check, not an input'); }
    if(DISP[st.country]) out+=DISP[st.country].vals.slice(1).map(v=>'<a class="item stale" href="'+v.url+'" target="_blank" rel="noopener">'+
      '<span class="itemHead">'+v.src+'</span><span class="itemBody">Competing estimate: '+fmtP(v.twh)+' TWh, '+nf(v.pct,1)+'% of national electricity</span>'+
      '<span class="itemMeta">'+v.yr+' · not used, shown for contrast</span></a>').join('');
  } else {
    out+=item('iea','capacity and demand, 2024')+item('kf','Q2 2026')+item('cbre','Q1 2026')+item('epoch','continuously updated')+item('owidci')+item('owidgen')+item('owidco2')+item('egrid')+item('avert','US new load at margin');
    out+=item('lbnl','validation anchor')+item('cso','validation anchor')+item('cbs','validation anchor');
  }
  return out || '<p class="empty">No distinct sources for this selection.</p>';
}
function tabReg(){
  const list=regsFor();
  if(!list.length) return '<p class="empty">No regulatory filing mapped to this selection. Try the United States, Ireland, or a campus like Meta Hyperion or Colossus.</p>';
  return list.map(r=>'<a class="item" href="'+r.url+'" target="_blank" rel="noopener">'+
    '<span class="itemHead">'+r.head+'</span>'+
    '<span class="itemBody">'+r.body_text.replace(/\*([^*]+)\*/g,'<em>$1</em>')+'</span>'+
    '<span class="itemMeta">'+r.place+' · '+r.body+' · '+r.ref+' · '+r.date+'</span></a>').join('');
}
function tabAcc(){
  const K={iea:st.kIea, metro:st.kNat};
  const rows=ANCH.map(a=>{const used=K[a.basis], model=a.cap*8760*used/1e6, d=(model-a.meas)/a.meas*100;
    return {a,model,d};});
  const dis = DISP[st.country];
  if(dis){
    const c=countryStats(st.country), nat=NAT[st.country], ov=OVR[st.country];
    const iea=D.regions.find(r=>r.iso.indexOf(st.country)>=0);
    const lf = ov && iea ? ov.twh*1e6/(iea.gw*1000*8760) : null;
    return '<p class="note warn" style="margin:0 0 10px"><b>Estimates disagree by '+
      nf(dis.vals[dis.vals.length-1].twh/dis.vals[0].twh,1)+'×.</b>'+
      (ov?' Using '+ov.src.split(',')[0]+'.':'')+'</p>'+
      (lf?'<p class="note">'+fmtP(ov.twh)+' TWh against the IEA&rsquo;s '+nf(iea.gw,1)+' GW of counted capacity implies a load factor of <b>'+nf(lf,2)+
       '</b> — physically impossible. Nothing draws '+Math.round(lf*100)+'% of nameplate every hour of the year. That is the proof the two sources count different facilities, not the same ones differently.</p>':'')+
      '<table class="mini"><thead><tr><th>Estimate</th><th class="num">TWh</th><th class="num">of national</th></tr></thead><tbody>'+
      '<tr><td><b>This model</b></td><td class="num">'+fmtP(c.twh)+'</td><td class="num">'+nf(c.twh/nat[0]*100,1)+'%</td></tr>'+
      dis.vals.map(v=>'<tr><td><a href="'+v.url+'" target="_blank" rel="noopener">'+v.src+'</a><br><span style="color:var(--muted)">'+v.yr+'</span></td>'+
        '<td class="num">'+fmtP(v.twh)+'</td><td class="num">'+nf(v.pct,1)+'%</td></tr>').join('')+
      '</tbody></table><p class="note">'+dis.note+'</p>';
  }
  const mine = st.country!=='all' && MEAS[st.country];
  let head='';
  if(mine){ const c=countryStats(st.country), M=MEAS[st.country], d=(c.twh-M.twh)/M.twh*100;
    head='<div class="kv"><span>This model says</span><b>'+fmtP(c.twh)+' TWh/yr</b></div>'+
      '<div class="kv"><span>'+M.src+' measured</span><b>'+fmtP(M.twh)+' TWh · '+M.yr+'</b></div>'+
      '<div class="kv"><span>Error</span><b style="color:'+(Math.abs(d)<10?'var(--s1)':'var(--s3)')+'">'+(d>=0?'+':'')+nf(d,0)+'%</b></div>'+
      '<p class="note">A live check, not an input — the model does not use this figure.</p><div style="height:14px"></div>';
  }
  return head+
    '<table class="mini"><thead><tr><th>Anchor</th><th class="num">measured</th><th class="num">implied</th><th class="num">used</th><th class="num">off by</th></tr></thead><tbody>'+
    rows.map(x=>'<tr><td><b>'+x.a.place+'</b><br><span style="color:var(--muted)">'+x.a.msrc+' · '+x.a.myr+'</span></td>'+
      '<td class="num">'+fmtP(x.a.meas)+'</td><td class="num">'+nf(x.a.implied,3)+'</td>'+
      '<td class="num">'+nf(K[x.a.basis],3)+'</td>'+
      '<td class="num" style="color:'+(Math.abs(x.d)<10?'var(--ink2)':'var(--s3)')+'">'+(x.d>=0?'+':'')+nf(x.d,0)+'%</td></tr>').join('')+
    '</tbody></table>'+
    '<p class="note">Five places measure data centre electricity rather than estimate it. Every parameter here is set from these, not from judgement. They split by which capacity dataset they divide into — IEA-basis implies 0.388–0.408, metro-basis 0.658–0.702 — which is why each layer carries its own factor. France was added after the factors were fixed, so it is an out-of-sample check rather than an input.</p>'+
    polBlock()+ vintBlock()+ avertBlock()+
    '<p class="note warn">The world row above is the IEA-basis check. The headline world total is higher than the IEA&rsquo;s 415 TWh because China is counted on its own national statistics (260 TWh) rather than the IEA&rsquo;s 100 TWh. That is deliberate: China&rsquo;s own number is better evidenced, at the cost of comparability.</p>'+
    '<p class="note">The load factor is the well-constrained part. The remaining error is capacity coverage: how much of a country&#39;s estate the mapped metros contain. Trust the world and US figures to roughly ±10%; treat other countries as floors.</p>';
}
function polBlock(){
  if(!POLICY.rule) return '';
  const row=(a)=>'<tr><td><b>'+a.place+'</b><br><span style="color:var(--muted)">'+a.body+' · '+a.fig+'</span></td>'+
    '<td class="num">'+nf(a.lf,3)+'</td><td><span class="pill '+(a.role==='override'?'pillWarn':'')+'">'+a.role+'</span><br><span style="color:var(--muted)">'+a.why+'</span></td></tr>';
  const rej=(r)=>'<tr><td><b>'+r.place+'</b><br><span style="color:var(--muted)">'+r.fig+'</span></td>'+
    '<td><span class="pill pillOut">out</span> '+r.test+'</td><td><span style="color:var(--muted)">'+r.why+'</span></td></tr>';
  return '<details class="pol"><summary>Which national sources are allowed to override the IEA — and which are not</summary>'+
    POLICY.rule.map(t=>'<p class="note">'+t+'</p>').join('')+
    '<table class="mini pol2"><thead><tr><th>Admitted</th><th class="num">load factor</th><th>role</th></tr></thead><tbody>'+
    POLICY.admitted.map(row).join('')+'</tbody></table>'+
    '<table class="mini pol2"><thead><tr><th>Rejected</th><th>fails</th><th>why</th></tr></thead><tbody>'+
    POLICY.rejected.map(rej).join('')+'</tbody></table></details>';
}
function vintBlock(){
  if(!VINT) return '';
  const pc=VINT.staleMw/VINT.totMw*100;
  return '<p class="note warn"><b>'+nf(pc,1)+'% of mapped metro capacity still rests on 2023 figures</b> — '+
    fmtP(VINT.staleMw)+' MW across '+VINT.n+' markets ('+VINT.names.slice(0,6).join(', ')+
    (VINT.names.length>6?' and '+(VINT.names.length-6)+' more':'')+'). '+
    'Cushman &amp; Wakefield stopped printing per-market operational MW after the 2023 edition, and the successor tables sit behind gated reports. Where a current figure exists it has been used; where none does, the 2023 value is carried and dated rather than quietly extrapolated.</p>';
}
function avertBlock(){
  const n = NEWLOAD.USA, a = n && n.avert;
  if(!a) return '';
  const rows = Object.entries(a.rates).sort((x,y)=>y[1]-x[1]).map(([k,v])=>
    '<tr><td>'+k+'</td><td class="num">'+Math.round(v)+'</td><td class="num">'+
    Math.round(0.48*506.25+0.52*v)+'</td></tr>').join('');
  return '<h4 style="margin-top:18px">US new load is priced at the margin</h4>'+
    '<p class="note">Average grid intensity answers &ldquo;what does the fleet emit?&rdquo;. The question a new data centre poses is &ldquo;which generator ramps to serve it?&rdquo;, and the answer is almost always gas. '+
    'Each US campus now uses the EPA AVERT marginal rate for its region ('+a.year+', '+a.profile+' profile) for the '+
    Math.round((1-0.48)*100)+'% of new capacity that draws on the ordinary grid. The other 48% arrives with its own generation and is priced as built. '+
    'Site values run <b>'+a.lo+'&ndash;'+a.hi+' g/kWh</b> across '+a.sites+' campuses, against the single <b>'+n.flat+' g/kWh</b> used before.</p>'+
    '<table class="mini"><thead><tr><th>AVERT region</th><th class="num">marginal</th><th class="num">new load</th></tr></thead><tbody>'+rows+'</tbody></table>'+
    '<p class="note">Weighting: the country figure is '+a.wpipe+' g/kWh, the mean across sites weighted by announced pipeline MW. Weighting by operational MW instead gives '+a.wop+
    ' g/kWh, a '+nf(Math.abs(a.wpipe-a.wop)/a.wpipe*100,1)+'% difference, so the choice of weight is not load-bearing.</p>'+
    '<p class="note warn"><b>Three limits, stated plainly.</b> '+
    'AVERT regions do not follow state lines. '+a.split+' of '+a.sites+' campuses sit in split states, '+fmtP(a.splitmw)+' MW of the '+fmtP(a.pipemw)+
    ' MW US pipeline; each is assigned by its eGRID subregion, and reassigning every one of them to its alternative region moves the US figure by 0.3%. '+
    'AVERT reports CO&#8322;, not CO&#8322;e, while the grid-average rates here are CO&#8322;e, so the marginal side is understated by a low single-digit percentage. '+
    'And AVERT is calibrated for modest load changes relative to system size: a multi-GW campus may sit outside the range where its regression holds, which makes this better evidenced than a national average but still not a dispatch model.</p>'+
    '<p class="note">Outside the US the grid average still stands, because no comparable free marginal dataset exists. A mixed basis is only defensible if it is declared, so it is declared here.</p>';
}
function tabRank(){
  const list=listForCharts().slice(0,14);
  if(!list.length) return '<p class="empty">Nothing matches these filters.</p>';
  const max=list[0].mt;
  return '<p class="note" style="margin:0 0 10px">Million tonnes CO₂ per year</p><div class="bars">'+list.map(x=>
    '<div class="bar" data-k="'+x.key+'" tabindex="0" role="button">'+
      '<span class="bn">'+x.n+'</span><span class="bv">'+fmtP(x.mt)+'</span>'+
      '<span class="track"><span class="fill" style="width:'+(x.mt/max*100).toFixed(1)+'%"></span></span></div>').join('')+'</div>';
}
const TABS={data:tabData, src:tabSrc, reg:tabReg, acc:tabAcc, rank:tabRank};
function renderRail(){
  const s=scopeStats();
  document.getElementById('scopeName').textContent=s.name;
  document.getElementById('resetScope').hidden=(s.kind==='world');
  const host=document.getElementById('tabBody');
  host.innerHTML=(TABS[st.tab]||tabData)();
  host.querySelectorAll('.bar').forEach(el=>{
    const pick=()=>{ const it=listForCharts().find(z=>z.key===el.dataset.k); if(!it) return; it.ref?selectMark(it.ref):selectRegion(it.reg); };
    el.onclick=pick; el.onkeydown=e=>{ if(e.key==='Enter'||e.key===' '){e.preventDefault();pick();} };
  });
}

function render(){ paintCountries(); renderMarks(); renderTiles(); renderRail(); }

document.querySelectorAll('.seg [data-sc]').forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll('.seg [data-sc]').forEach(x=>x.setAttribute('aria-pressed', String(x===b)));
    st.scenario=b.dataset.sc; render();
  };
});
const bind=(id,fn)=>{ const el=document.getElementById(id); el.addEventListener('input',()=>{fn(el); render();}); return el; };
bind('lySites',el=>st.sites=el.checked);
bind('lyMetros',el=>st.metros=el.checked);
bind('lyGrid',el=>st.grid=el.checked);
bind('fStatus',el=>st.status=el.value);
bind('fOp',el=>st.op=el.value);
bind('fSearch',el=>st.q=el.value.trim());
document.getElementById('fCountry').addEventListener('change',e=>{
  const v=e.target.value;
  if(v==='all'){ clearScope(); } else { selectCountry(v); }
});
document.getElementById('fCountry').insertAdjacentHTML('beforeend',
  countriesWithData().map(c=>'<option value="'+c+'">'+(NAMES[c]||c)+'</option>').join(''));
const ops=[...new Set(D.sites.map(s=>s.o||'—'))].sort();
document.getElementById('fOp').insertAdjacentHTML('beforeend', ops.map(o=>'<option value="'+o+'">'+o+'</option>').join(''));

const sl=(id,vid,fn,fmt)=>{ const el=document.getElementById(id), v=document.getElementById(vid);
  el.addEventListener('input',()=>{ fn(parseFloat(el.value)); v.textContent=fmt(parseFloat(el.value)); render(); }); };
sl('sKIea','vKIea',x=>st.kIea=x, x=>x.toFixed(3));
sl('sKMetro','vKMetro',x=>st.kMetro=x, x=>x.toFixed(2));
sl('sKNat','vKNat',x=>st.kNat=x, x=>x.toFixed(2));
sl('sKAi','vKAi',x=>st.kAi=x, x=>x.toFixed(2));
sl('sGrid','vGrid',x=>st.cut=x/100, x=>x+'%');
sl('sGrow','vGrow',x=>st.grow=x/100, x=>'+'+x+'%');
document.getElementById('mMarg').addEventListener('change',e=>{ st.marg=e.target.checked; render(); });
document.getElementById('resetAssume').onclick=()=>{
  st.kIea=.398; st.kMetro=.60; st.kNat=.70; st.kAi=.70; st.cut=0; st.grow=.21; st.marg=true;
  sKIea.value=.398; sKMetro.value=.60; sKNat.value=.70; sKAi.value=.70; sGrid.value=0; sGrow.value=21; mMarg.checked=true;
  vKIea.textContent='0.398'; vKMetro.textContent='0.60'; vKNat.textContent='0.70'; vKAi.textContent='0.70'; vGrid.textContent='0%';
  vGrow.textContent='+21%';
  render();
};

document.querySelectorAll('.tabs [data-tab]').forEach(b=>{
  b.onclick=()=>{ st.tab=b.dataset.tab;
    document.querySelectorAll('.tabs [data-tab]').forEach(x=>x.setAttribute('aria-selected', String(x===b)));
    renderRail(); };
});
function toggleDrawer(id,btn){
  const d=document.getElementById(id), open=d.hidden;
  document.querySelectorAll('.drawer').forEach(x=>x.hidden=true);
  document.querySelectorAll('#assumeBtn,#methodBtn').forEach(x=>x.setAttribute('aria-expanded','false'));
  d.hidden=!open; btn.setAttribute('aria-expanded', String(open));
  if(open) d.scrollIntoView({block:'nearest',behavior:'smooth'});
}
document.getElementById('assumeBtn').onclick=e=>toggleDrawer('assumeDrawer',e.currentTarget);
document.getElementById('methodBtn').onclick=e=>toggleDrawer('methodDrawer',e.currentTarget);
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>{
  document.getElementById(b.dataset.close).hidden=true;
  document.querySelectorAll('#assumeBtn,#methodBtn').forEach(x=>x.setAttribute('aria-expanded','false'));
});

const tbn=document.getElementById('themeBtn');
tbn.onclick=()=>{
  const cur=document.documentElement.getAttribute('data-theme');
  const sysDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
  const next = cur ? (cur==='dark'?'light':'dark') : (sysDark?'light':'dark');
  document.documentElement.setAttribute('data-theme',next);
  try{ localStorage.setItem('dcpa-theme',next); }catch(e){}
};
try{ const t=localStorage.getItem('dcpa-theme'); if(t) document.documentElement.setAttribute('data-theme',t); }catch(e){}

(function(){
  const b=D.meta&&D.meta.built; if(!b) return;
  const d=new Date(b+'T12:00:00Z');
  const f=x=>x.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric',timeZone:'UTC'});
  const days=Math.floor((Date.now()-d.getTime())/864e5);
  const el=document.getElementById('freshness');
  if(!el) return;
  // The page reports its own staleness rather than asserting currency: if the
  // daily job stops running, that shows here instead of going unnoticed.
  if(days>3) el.innerHTML='Refreshed <b>'+f(d)+'</b> · <b style="color:var(--s3)">'+days+
    ' days ago — the daily refresh has not run</b> · treat every figure as of that date';
  else el.innerHTML='Refreshed <b>'+f(d)+'</b>'+(days>0?' · '+days+'d ago':'')+
    ' · checked daily · sources and vintages under Sources';
})();
svg.addEventListener('click',e=>{ if(e.target===svg && !(drag&&drag.moved)) clearScope(); });
render();
})();

