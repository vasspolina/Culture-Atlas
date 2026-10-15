// Money maps. Reads assets/money-maps.json (built by tools/build_money_maps.py) and draws one map per record.
fetch('assets/money-maps.json').then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); }).then(D=>{
const byRec=Object.fromEntries(D.map(r=>[r.id,r]));
const CAT={gov:{label:'Government & public',color:'#3a5cf8'},corp:{label:'Corporate & sponsors',color:'#a9e0e6'},found:{label:'Foundations & donors',color:'#ee6c38'},flag:{label:'Flagged on record',color:'#ec4fe8'},link:{label:'Also funds',color:'#c6b566'}};
const CATS=['gov','corp','found','flag','link'];
const TIER={A:'Clean',B:'Flagged',U:'Unverified'};
const on={gov:true,corp:true,found:true,flag:true,link:true};
let seed=7; const rnd=()=>{ seed=(seed*16807)%2147483647; return (seed-1)/2147483646; };
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const host=u=>{ try{ return new URL(u).hostname.replace(/^www\./,''); }catch(e){ return u; } };
const svg=d3.select('#map');
// ---------- 3D space: circles sit on depth layers inside a room (floor, back wall, poles); drag the background to orbit ----------
const FOC=2600; let YAW=0.5, PITCH=0.24, SPIN=true, spinRunning=false, spinStart=0, REDRAW=null, ORB=null, orbMoved=0;
function rot(x,y,z){ const cy=Math.cos(YAW), sy=Math.sin(YAW), cp=Math.cos(PITCH), sp=Math.sin(PITCH);
  const x1=x*cy+z*sy, z1=-x*sy+z*cy, y1=y*cp-z1*sp, z2=y*sp+z1*cp; return [x1,y1,z2]; }
let DOLLY=0; const NEAR=320; const persp=z=>FOC/Math.max(NEAR,FOC-DOLLY-z); const seen=z=>FOC-DOLLY-z>NEAR;
function gproj(x,y){ return [x,y]; }
function ginv(X,Y,d){ const s=d.s||1, x1=X/s, yp=Y/s, z2=d.dz||0, cy=Math.cos(YAW), sy=Math.sin(YAW), cp=Math.cos(PITCH), sp=Math.sin(PITCH);
  const y1=yp*cp+z2*sp, z1=-yp*sp+z2*cp; return [x1*cy-z1*sy, y1]; }
const depthOp=z=>Math.max(.18,Math.min(1,.62+z/1100));
const ROOM={Y:720,Z:1300,X:1700};
function guides(N){ const vis=r=>FOC-DOLLY-r[2]>NEAR, Pt=(x,y,z)=>{ const r=rot(x,y,z); return vis(r)?[r[0]*persp(r[2]),r[1]*persp(r[2])]:null; };
  const seg=(a,b)=>{ const p=Pt(a[0],a[1],a[2]), q=Pt(b[0],b[1],b[2]); return p&&q?'M'+p[0].toFixed(1)+','+p[1].toFixed(1)+'L'+q[0].toFixed(1)+','+q[1].toFixed(1):''; };
  const {X,Y,Z}=ROOM; let floor='',wall='',poles='';
  for(let z=-Z;z<=Z;z+=260) floor+=seg([-X,Y,z],[X,Y,z]);
  for(let x=-X;x<=X;x+=340) floor+=seg([x,Y,-Z],[x,Y,Z]);
  for(let x=-X;x<=X;x+=340) wall+=seg([x,-Y*1.4,-Z],[x,Y,-Z]);
  for(let y=-Y*1.4;y<=Y;y+=260) wall+=seg([-X,y,-Z],[X,y,-Z]);
  N.forEach(n=>{ if(!n.center) poles+=seg([n.x,n.y,n.z||0],[n.x,Y,n.z||0]); });
  return {floor,wall,poles}; }
function drawGlobe(sel){ sel.selectAll('*').remove(); }
function updateGuides(sel,N){}
// ---------- sea-plant sway: a touch sends a small wave outward; every circle has its own spring, so each moves on its own ----------
window.__AR=1; let SWAYNODES=()=>[], SWAYLINKS=()=>[], swayRun=false, swayLast=0, swayThrottle=0;
const REDUCE=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function swayKick(cx,cy,power){ const svgN=document.querySelector('#map'); if(!svgN) return; const rc=svgN.getBoundingClientRect(), t=d3.zoomTransform(svgN), now=performance.now();
  SWAYNODES().forEach(d=>{ if(d.px==null) return; const X=t.x+d.px*t.k*window.__AR+rc.left, Y=t.y+d.py*t.k+rc.top, dist=Math.hypot(X-cx,Y-cy);
    if(d.sk==null){ d.sk=0.0035+rnd()*0.004; d.sc=0.035+rnd()*0.03; d.sa=rnd()*6.283; d.sz=(rnd()-.5); d.ox=d.oy=d.oz=d.vx=d.vy=d.vz=0; }
    const fall=1/(1+dist/420), amp=power*(6+rnd()*11)*(0.45+fall)*(dist<70?1.7:1), ang=d.sa+(rnd()-.5)*1.1;
    d.pend={t:now+dist*1.1+rnd()*120,ax:Math.cos(ang)*amp*(d.center?0.15:1),ay:Math.sin(ang)*amp*0.8*(d.center?0.15:1),az:d.sz*amp*1.2*(d.center?0.15:1)}; });
  SWAYLINKS().forEach(l=>{ if(l.source.px==null||l.target.px==null) return;
    if(l.sk==null){ l.sk=0.0025+rnd()*0.003; l.sc=0.04+rnd()*0.03; l.sk2=0.003+rnd()*0.003; l.sc2=0.04+rnd()*0.03; l.la=l.lb=l.lva=l.lvb=0; }
    const X=t.x+((l.source.px+l.target.px)/2)*t.k*window.__AR+rc.left, Y=t.y+((l.source.py+l.target.py)/2)*t.k+rc.top, dist=Math.hypot(X-cx,Y-cy), fall=1/(1+dist/420), amp=power*(5+rnd()*11)*(0.5+fall)*(dist<90?1.6:1), sg=rnd()<.5?-1:1;
    l.pend={t:now+dist*1.0+rnd()*200,a:sg*amp,b:-sg*amp*(0.5+rnd()*0.9)}; });
  if(!swayRun){ swayRun=true; swayLast=performance.now(); requestAnimationFrame(swayLoop); } }
function swayLoop(){ const now=performance.now(), dt=Math.min(2.5,(now-swayLast)/16.7); swayLast=now; let live=false;
  SWAYNODES().forEach(d=>{ if(d.sk==null) return;
    if(d.pend&&now>=d.pend.t){ d.vx+=d.pend.ax*0.17; d.vy+=d.pend.ay*0.17; d.vz+=d.pend.az*0.17; d.pend=null; }
    if(d.pend){ live=true; }
    d.vx+=(-d.sk*d.ox-d.sc*d.vx)*dt; d.vy+=(-d.sk*d.oy-d.sc*d.vy)*dt; d.vz+=(-d.sk*d.oz-d.sc*d.vz)*dt;
    d.ox+=d.vx*dt; d.oy+=d.vy*dt; d.oz+=d.vz*dt;
    if(Math.abs(d.ox)+Math.abs(d.oy)+Math.abs(d.oz)+Math.abs(d.vx)+Math.abs(d.vy)+Math.abs(d.vz)>0.04) live=true; else { d.ox=d.oy=d.oz=d.vx=d.vy=d.vz=0; } });
  SWAYLINKS().forEach(l=>{ if(l.sk==null) return;
    if(l.pend&&now>=l.pend.t){ l.lva+=l.pend.a*0.1; l.lvb+=l.pend.b*0.1; l.pend=null; }
    if(l.pend) live=true;
    l.lva+=(-l.sk*l.la-l.sc*l.lva)*dt; l.lvb+=(-l.sk2*l.lb-l.sc2*l.lvb)*dt; l.la+=l.lva*dt; l.lb+=l.lvb*dt;
    if(Math.abs(l.la)+Math.abs(l.lb)+Math.abs(l.lva)+Math.abs(l.lvb)>0.04) live=true; else { l.la=l.lb=l.lva=l.lvb=0; } });
  if(REDRAW) REDRAW();
  if(live) requestAnimationFrame(swayLoop); else swayRun=false; }
window.addEventListener('pointerdown',e=>{ if(e.target&&e.target.closest&&e.target.closest('#map')) swayKick(e.clientX,e.clientY,1); });
window.addEventListener('pointermove',e=>{ if(!e.buttons&&e.pointerType!=='touch') return; if(!e.target||!e.target.closest||!e.target.closest('#map')) return; const now=performance.now(); if(now-swayThrottle<70) return; swayThrottle=now; swayKick(e.clientX,e.clientY,0.55); });
const zfilter=()=>false;
function spinLoop(){ if(!SPIN||!REDRAW){ spinRunning=false; return; } YAW+=0.001; REDRAW(); if(performance.now()-spinStart>9000){ SPIN=false; spinRunning=false; return; } requestAnimationFrame(spinLoop); }
function startSpin(){ if(REDUCE){ SPIN=false; return; } SPIN=true; spinStart=performance.now(); if(!spinRunning){ spinRunning=true; requestAnimationFrame(spinLoop); } }
// one finger or mouse drag turns the scene; two fingers pinch to fly through it and slide; wheel and W/S fly; arrows turn
const PTR=new Map(); let PREV=null, PANBY=()=>{};
const clampD=v=>Math.max(-2600,Math.min(2300,v)), clampP=v=>Math.max(-1.25,Math.min(1.25,v));
function bindOrbit(svgSel){
  svgSel.on('pointerdown.orbit',e=>{ if(e.target.closest&&e.target.closest('g[tabindex]')) return; PTR.set(e.pointerId,{x:e.clientX,y:e.clientY}); orbMoved=0; SPIN=false; PREV=null; })
    .on('wheel.dolly',e=>{ e.preventDefault(); SPIN=false; DOLLY=clampD(DOLLY-e.deltaY*(e.ctrlKey?6:1.6)); REDRAW&&REDRAW(); },{passive:false});
}
window.addEventListener('pointermove',e=>{ if(!PTR.has(e.pointerId)||!REDRAW) return; const p=PTR.get(e.pointerId), dx=e.clientX-p.x, dy=e.clientY-p.y; p.x=e.clientX; p.y=e.clientY; orbMoved+=Math.abs(dx)+Math.abs(dy);
  if(PTR.size>=2){ const a=[...PTR.values()], d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y), mx=(a[0].x+a[1].x)/2, my=(a[0].y+a[1].y)/2;
    if(PREV){ DOLLY=clampD(DOLLY+(d-PREV.d)*5); PANBY(mx-PREV.mx,my-PREV.my); } PREV={d,mx,my}; REDRAW(); return; }
  PREV=null;
  if(e.shiftKey||e.buttons===4||e.buttons===2) PANBY(dx,dy); else { YAW+=dx*0.006; PITCH=clampP(PITCH+dy*0.006); }
  REDRAW(); });
['pointerup','pointercancel'].forEach(t=>window.addEventListener(t,e=>{ PTR.delete(e.pointerId); PREV=null; }));
window.addEventListener('keydown',e=>{ if(!REDRAW||e.altKey||e.ctrlKey||e.metaKey) return; const t=e.target; if(t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA')) return; const k=e.key; let used=true;
  if(k==='ArrowLeft') YAW-=0.07; else if(k==='ArrowRight') YAW+=0.07; else if(k==='ArrowUp') PITCH=clampP(PITCH-0.06); else if(k==='ArrowDown') PITCH=clampP(PITCH+0.06);
  else if(k==='w'||k==='W') DOLLY=clampD(DOLLY+150); else if(k==='s'||k==='S') DOLLY=clampD(DOLLY-150); else used=false;
  if(used){ e.preventDefault(); SPIN=false; REDRAW(); } });


// hairline with uneven pressure, pointed at both ends
function blade(pts,W,pk){
  const n=pts.length; if(n<3) return '';
  const L=[],R=[]; const k=Math.log(0.5)/Math.log(pk);
  for(let i=0;i<n;i++){
    const p=pts[Math.max(0,i-1)], q=pts[Math.min(n-1,i+1)];
    let tx=q[0]-p[0], ty=q[1]-p[1]; const m=Math.hypot(tx,ty)||1; tx/=m; ty/=m;
    const t=i/(n-1), tt=Math.pow(t,k), w=W*Math.pow(Math.sin(Math.PI*tt),0.45)/2;
    L.push([pts[i][0]-ty*w,pts[i][1]+tx*w]); R.push([pts[i][0]+ty*w,pts[i][1]-tx*w]);
  }
  return 'M'+L.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join('L')+'L'+R.reverse().map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join('L')+'Z';
}
function inkPath(pts,wfn){
  const n=pts.length; if(n<3) return '';
  const L=[],R=[];
  for(let i=0;i<n;i++){
    const p=pts[Math.max(0,i-1)], q=pts[Math.min(n-1,i+1)];
    let tx=q[0]-p[0], ty=q[1]-p[1]; const m=Math.hypot(tx,ty)||1; tx/=m; ty/=m;
    const w=wfn(i/(n-1))/2;
    L.push([pts[i][0]-ty*w,pts[i][1]+tx*w]); R.push([pts[i][0]+ty*w,pts[i][1]-tx*w]);
  }
  return 'M'+L.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join('L')+'L'+R.reverse().map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join('L')+'Z';
}
// a circle drawn in one pass: starts thin, swells, overshoots its start and drifts slightly off
function loop(r,W){
  const a0=rnd()*6.28, turns=1.04+rnd()*0.09, drift=(rnd()-0.5)*0.13, p1=rnd()*6.28, p2=rnd()*6.28, N=80, pts=[];
  for(let i=0;i<=N;i++){ const t=i/N, th=a0+t*turns*Math.PI*2, rr=r*(1+drift*(t-0.5)+0.012*Math.sin(2*th+p1)+0.008*Math.sin(3*th+p2));
    pts.push([Math.cos(th)*rr,Math.sin(th)*rr]); }
  return inkPath(pts,t=>W*(0.12+0.88*Math.pow(Math.sin(Math.PI*Math.pow(t,0.8)),0.6)));
}
// faint partial second pass
function trace(r){
  const a0=rnd()*6.28, span=(0.25+rnd()*0.4)*Math.PI*2, rr0=r*(0.95+rnd()*0.07), pts=[];
  for(let i=0;i<=30;i++){ const th=a0+i/30*span; pts.push([Math.cos(th)*rr0,Math.sin(th)*rr0]); }
  return inkPath(pts,t=>0.9*Math.sin(Math.PI*t));
}
// MoMA as a tangled hand-inked globe: long elliptical arcs crossed by many fine hair strokes, whiskers at the top
function building(el,col){
  const R=150, put=(pts,W,pk)=>el.append('path').attr('d',blade(pts,W,pk)).attr('fill',col);
  const arc=(cx,cy,rx,ry,a0,a1,rot,n)=>{ const out=[]; for(let i=0;i<=n;i++){ const a=a0+(a1-a0)*i/n, x=rx*Math.cos(a), y=ry*Math.sin(a); out.push([cx+x*Math.cos(rot)-y*Math.sin(rot), cy+x*Math.sin(rot)+y*Math.cos(rot)]); } return out; };
  const jit=()=>(rnd()-0.5)*0.06;
  // meridians: tall ellipses of different widths
  [1,0.86,0.66,0.4,0.16].forEach(k=>{ put(arc(0,0,R*k*(0.98+rnd()*0.04),R*1.12,0.1+jit(),Math.PI*2-0.1+jit(),jit(),70),3.4+rnd()*1.4,0.5); });
  // parallels: curved bands bowing downward, drawn heavier
  [-0.62,-0.4,-0.18,0,0.2,0.42,0.66].forEach(f=>{ const y=f*R*1.12, w=R*Math.sqrt(Math.max(0.02,1-f*f))*1.02, bow=R*(0.1+0.07*Math.abs(f));
    const pts=[]; for(let i=0;i<=40;i++){ const t=i/40*2-1; pts.push([t*w, y+bow*(1-t*t)*(f<0?0.5:1)+(rnd()-0.5)*1.6]); } put(pts,2.8+rnd()*1.8,0.5); });
  // fine hair strokes flowing mostly vertically, bunching toward the top
  for(let i=0;i<150;i++){
    const x0=(rnd()-0.5)*2*R*0.98, ang=(rnd()-0.5)*0.55, L=70+rnd()*190, y0=-R*1.1+rnd()*R*1.7, bend=(rnd()-0.5)*0.35, pts=[];
    for(let k=0;k<=18;k++){ const t=k/18; pts.push([x0+Math.sin(ang)*L*t+bend*L*t*t*(1-0.2*t), y0+Math.cos(ang)*L*t]); }
    put(pts,0.7+rnd()*1.1,0.2+rnd()*0.6);
  }
  // whiskers sweeping out from the top
  for(let i=0;i<22;i++){
    const a=-Math.PI/2+(rnd()-0.5)*2.4, L=45+rnd()*95, x0=(rnd()-0.5)*50, y0=-R*1.05+rnd()*20, bend=(rnd()-0.5)*0.5, pts=[];
    for(let k=0;k<=14;k++){ const t=k/14, aa=a+bend*t; pts.push([x0+Math.cos(aa)*L*t, y0+Math.sin(aa)*L*t]); }
    put(pts,0.8+rnd()*0.9,0.3);
  }
}

let cur=null;
function render(inst){
  if(cur) cur.stop();
  svg.selectAll('*').remove(); svg.on('.zoom',null).on('click',null);
  seed=1; for(const ch of inst.id) seed=(seed*31+ch.charCodeAt(0))%2147483646+1;
  // ---------- data ----------
  const idOf=i=>i===0?'c':'n'+i;
  const N=[{id:'c',label:inst.n,cat:'center',tier:5,center:true}];
  inst.nodes.forEach((n,i)=>N.push({id:'n'+(i+1),label:n[0],cat:n[1],tier:n[2],note:n[3],go:n[4]||''}));
  const E=inst.edges.map(e=>[idOf(e[0]),idOf(e[1]),e[2]]);
  const byId=Object.fromEntries(N.map(n=>[n.id,n]));
  const links=E.map(([s,t,l])=>({source:s,target:t,label:l}));
  const toC=new Set(E.filter(e=>e[0]==='c'||e[1]==='c').map(e=>e[0]==='c'?e[1]:e[0]));
  // ---------- polar layout ----------
  const SECT={found:[-64,26],flag:[34,118],gov:[128,220],corp:[228,330],link:[0,360]}, R={5:0,3:340,2:430,1:520};
  Object.keys(SECT).forEach(c=>{
    const list=N.filter(n=>n.cat===c&&toC.has(n.id)).sort((a,b)=>b.tier-a.tier); if(!list.length) return;
    const [a0,a1]=SECT[c]; list.forEach((n,i)=>{ n.ang=(a0+(a1-a0)*((i+0.5)/list.length))*Math.PI/180; n.r=R[n.tier]+((i%2)?30:0); });
  });
  N.forEach(n=>{ if(n.center){ n.tx=n.ty=0; n.fx=0; n.fy=0; } else if(n.r!=null){ n.tx=Math.cos(n.ang)*n.r; n.ty=Math.sin(n.ang)*n.r; } });
  for(let pass=0;pass<3;pass++) N.filter(n=>!n.center&&n.r==null).forEach(n=>{
    const nb=E.filter(e=>e[0]===n.id||e[1]===n.id).map(e=>byId[e[0]===n.id?e[1]:e[0]]).filter(o=>!o.center&&o.r!=null); if(!nb.length) return;
    let sx=0,sy=0,rr=0; nb.forEach(o=>{ sx+=Math.cos(o.ang); sy+=Math.sin(o.ang); rr=Math.max(rr,o.r); });
    n.ang=Math.atan2(sy,sx)+(rnd()-.5)*.5; n.r=rr+120; n.tx=Math.cos(n.ang)*n.r; n.ty=Math.sin(n.ang)*n.r; });
  N.filter(n=>!n.center&&n.r==null).forEach(n=>{ n.ang=0; n.r=600; n.tx=600; n.ty=0; });
  const CR=26;
  const rad=n=>n.center?CR:({3:26,2:17,1:10})[n.tier];
  const colOf=n=>n.center?'#fff':CAT[n.cat].color;
  // ---------- svg ----------
  const defs=svg.append('defs'), bf=defs.append('filter').attr('id','bloom').attr('x','-20%').attr('y','-20%').attr('width','140%').attr('height','140%');
  bf.append('feGaussianBlur').attr('in','SourceGraphic').attr('stdDeviation',1.1).attr('result','b');
  bf.append('feMerge').selectAll('feMergeNode').data(['b','SourceGraphic']).join('feMergeNode').attr('in',d=>d);
  const globeG=svg.append('g'); drawGlobe(globeG);
  const lineG=svg.append('g'), g=svg.append('g').attr('filter','url(#bloom)');
  let AR=1, nodeSel, linkSel, sim;
  const zoom=d3.zoom().scaleExtent([.05,40]).filter(zfilter).on('zoom',e=>{ const t=`translate(${e.transform.x},${e.transform.y}) scale(${e.transform.k*AR},${e.transform.k})`; g.attr('transform',t); globeG.attr('transform',t); lineG.attr('transform',t); if(typeof nodeSel!=='undefined'&&nodeSel) fixLabels(); });
  const setAR=a=>{ AR=a; window.__AR=a; fixLabels(); };
  function fixLabels(){ const k=d3.zoomTransform(svg.node()).k||1, s=Math.max(.5,Math.min(2.6,15.6/(22*k))); nodeSel.select('text.lbl').attr('transform',`scale(${s/AR},${s})`); }
  svg.call(zoom);
  PANBY=(dx,dy)=>{ const k=d3.zoomTransform(svg.node()).k; svg.call(zoom.translateBy,dx/k,dy/k); };
  linkSel=lineG.selectAll('path').data(links).join('path').attr('stroke','none');
  linkSel.each(function(d){ const r=rnd(); d.kind=r<0.18?'line':(r<0.82?'arc':'s'); d.side=rnd()<0.5?1:-1; d.bend=d.kind==='line'?0.012*rnd():0.12+rnd()*0.22; d.bend2=0.08+rnd()*0.16; d.pk=0.2+rnd()*0.6; d.W=1.6+rnd()*2.0; if(rnd()<0.12) d.W*=1.9; d.gap=rnd()<0.14?(0.4+rnd()*0.3):0; d.dbl=rnd()<0.3?(d.side*(3+rnd()*5)):0; });
  const edgeCol=d=>d.label==='also funds'?CAT.link.color:colOf(byId[d.source.center||d.source==='c'?d.target.id||d.target:(d.source.id||d.source)]||byId[d.target.id||d.target]);
  function flow(d){ const W0=d.W*(((d.source.s||1)+(d.target.s||1))/2);
    const sx=d.source.px, sy=d.source.py, tx=d.target.px, ty=d.target.py, dx=tx-sx, dy=ty-sy, L=Math.hypot(dx,dy)||1, px=-dy/L*d.side, py=dx/L*d.side;
    const o1=L*d.bend+(d.la||0), o2=(d.kind==='s'?-1:1)*L*(d.kind==='line'?d.bend:d.bend2)+(d.lb||0);
    const c1=[sx+dx*0.3+px*o1,sy+dy*0.3+py*o1], c2=[sx+dx*0.7+px*o2,sy+dy*0.7+py*o2], rs=rad(d.source)*0.4, rt=rad(d.target)*0.4, pts=[];
    for(let i=0;i<=48;i++){ const t=i/48,u=1-t, x=u*u*u*sx+3*u*u*t*c1[0]+3*u*t*t*c2[0]+t*t*t*tx, y=u*u*u*sy+3*u*u*t*c1[1]+3*u*t*t*c2[1]+t*t*t*ty;
      if(Math.hypot(x-sx,y-sy)>rs&&Math.hypot(x-tx,y-ty)>rt) pts.push([x,y]); }
    if(pts.length<4) return '';
    let out; if(!d.gap) out=blade(pts,W0,d.pk); else { const k=Math.floor(pts.length*d.gap), gp=Math.max(1,Math.floor(pts.length*0.06)); out=blade(pts.slice(0,k),W0,d.pk)+blade(pts.slice(k+gp),W0,d.pk); }
    if(d.dbl){ const a=Math.floor(pts.length*0.06), b=Math.floor(pts.length*0.92), nx=-dy/L, ny=dx/L; out+=blade(pts.slice(a,b).map(p=>[p[0]+nx*d.dbl,p[1]+ny*d.dbl]),Math.max(0.8,W0*0.4),0.5); }
    return out;
  }
  nodeSel=g.append('g').selectAll('g').data(N).join('g').attr('cursor','pointer').attr('tabindex',0).attr('role','button').attr('aria-label',d=>d.label);
  nodeSel.append('title').text(d=>d.label+(d.note?' · '+d.note:''));
  nodeSel.each(function(d){
    const el=d3.select(this), r=rad(d);
    const W=d.center?2.9:{3:2.9,2:2.3,1:1.7}[d.tier], col=colOf(d);
    el.append('circle').attr('r',r*0.97).attr('fill','none').attr('pointer-events','all');
    el.append('path').attr('d',loop(r,W)).attr('fill',col);
    if(rnd()<0.6) el.append('path').attr('d',trace(r)).attr('fill',col).attr('opacity',.8);
  });
  nodeSel.append('text').attr('class','lbl').attr('fill','#fff').attr('font-size',22).attr('font-family','PP Neue Gstaad, sans-serif').attr('font-weight',400).attr('stroke','#000').attr('stroke-width',3).attr('paint-order','stroke').attr('pointer-events','none').attr('display','none').attr('y',d=>-rad(d)-8).attr('text-anchor','middle').text(d=>d.label);
  sim=d3.forceSimulation(N).force('x',d3.forceX(d=>d.tx).strength(d=>d.center?1:.35)).force('y',d3.forceY(d=>d.ty).strength(d=>d.center?1:.35))
    .force('collide',d3.forceCollide(d=>d.center?rad(d)+40:rad(d)+22).iterations(3))
    .force('link',d3.forceLink(links).id(d=>d.id).distance(130).strength(d=>(d.target.center||d.source.center)?0.02:0.6)).alphaDecay(.04).stop();
  sim.tick(220);
  const draw=()=>{ N.forEach(d=>{ const r=rot(d.x+(d.ox||0),d.y+(d.oy||0),(d.z||0)+(d.oz||0)), sc=persp(r[2]); d.px=r[0]*sc; d.py=r[1]*sc; d.s=sc; d.dz=r[2]; d.vis=seen(r[2]); }); linkSel.attr('d',flow).attr('visibility',l=>(l.source.vis&&l.target.vis)?null:'hidden').attr('fill-opacity',l=>depthOp((l.source.dz+l.target.dz)/2+DOLLY)); nodeSel.attr('transform',d=>`translate(${d.px},${d.py}) scale(${d.s})`).attr('visibility',d=>d.vis?null:'hidden').sort((a,b)=>a.dz-b.dz); nodeSel.each(function(d){ d3.select(this).selectAll('path').attr('fill-opacity',depthOp(d.dz+DOLLY)); }); updateGuides(globeG,N); };
  draw(); linkSel.attr('fill',d=>d.label==='also funds'?CAT.link.color:colOf(d.source.center?d.target:d.source)); sim.on('tick',draw);
  nodeSel.call(d3.drag().subject(d=>({x:d.px,y:d.py})).on('start',(e,d)=>{ if(!e.active) sim.alphaTarget(.2).restart(); d.fx=d.x; d.fy=d.y; }).on('drag',(e,d)=>{ const q=ginv(e.x,e.y); d.fx=q[0]; d.fy=q[1]; }).on('end',(e,d)=>{ if(!e.active) sim.alphaTarget(0); if(!d.center){ d.fx=null; d.fy=null; } }));
  // ---------- view: stretch to the canvas, spread evenly ----------
  let anim=null;
  const applyView=t=>{ setAR(t.ar); svg.call(zoom.transform,d3.zoomIdentity.translate(t.x,t.y).scale(t.k)); };
  function fit(animate){
    const w=svg.node().clientWidth,h=svg.node().clientHeight; if(!w||!h) return; let bx=null; try{ bx=g.node().getBBox(); }catch(err){}
    let target; const few=N.length<4;
    if(!bx||!(bx.width>0)||!(bx.height>0)) target={x:w/2,y:h/2,k:Math.min(w/1700,h/1450),ar:1};
    else { const topPad=(()=>{ const c=document.getElementById('cats'); return c?c.offsetHeight+4:0; })(), hh=Math.max(120,h-topPad), pad=6, sx=(w-2*pad)/bx.width, sy=(hh-2*pad)/bx.height, cx=bx.x+bx.width/2, cy=bx.y+bx.height/2;
      if(few){ const k=Math.min(sx,sy,1.2); target={x:w/2-cx*k,y:topPad+hh/2-cy*k,k,ar:1}; } else { const ar=(w<700?1:Math.max(.6,Math.min(2.2,sx/sy))), k=Math.min(sy,sx/ar); target={x:w/2-cx*k*ar,y:topPad+hh/2-cy*k,k,ar}; } }
    cancelAnimationFrame(anim);
    if(!animate){ applyView(target); return; }
    const c=d3.zoomTransform(svg.node()), from={x:c.x,y:c.y,k:c.k,ar:AR}, t0=performance.now();
    const step=now=>{ const u=Math.min(1,(now-t0)/800), e=d3.easeCubicInOut(u); applyView({x:from.x+(target.x-from.x)*e,y:from.y+(target.y-from.y)*e,k:from.k*Math.pow(target.k/from.k,e),ar:from.ar+(target.ar-from.ar)*e}); if(u<1) anim=requestAnimationFrame(step); };
    anim=requestAnimationFrame(step);
  }
  function relayout(){
    const ns=N.filter(d=>!d.center), n=ns.length; const PL={gov:-320,corp:-130,found:130,flag:330,link:520}; ns.forEach(d=>{ d.z=(PL[d.cat]||0)+(rnd()-0.5)*380+(d.tier-2)*70; }); if(n<3){ draw(); fit(); return; }
    const narrow=svg.node().clientWidth<700, H=1500, W=H*(narrow?Math.max(.55,Math.min(1,svg.node().clientWidth/Math.max(1,svg.node().clientHeight))):1.6), mx=90, ax=Math.max(...ns.map(d=>Math.abs(d.x)),1), ay=Math.max(...ns.map(d=>Math.abs(d.y)),1);
    ns.forEach(d=>{ d.bx=d.x; d.by=d.y; });
    [...ns].sort((a,b)=>a.bx-b.bx).forEach((d,i)=>d.ex=((i+.5)/n-.5)*(W-2*mx));
    [...ns].sort((a,b)=>a.by-b.by).forEach((d,i)=>d.ey=((i+.5)/n-.5)*(H-2*mx));
    ns.forEach(d=>{ d.tx=0.25*d.bx/ax*(W-2*mx)/2+0.75*d.ex; d.ty=0.25*d.by/ay*(H-2*mx)/2+0.75*d.ey; d.x=d.tx; d.y=d.ty; });
    sim.force('x').x(d=>d.tx); sim.force('y').y(d=>d.ty);
    sim.force('charge',d3.forceManyBody().strength(-30)).force('collide',d3.forceCollide(d=>d.center?rad(d)+40:rad(d)+34).iterations(3)).force('link').distance(400).strength(d=>(d.target.center||d.source.center)?0:0.008);
    sim.alpha(1).tick(240);
    ns.forEach(d=>{ d.x=Math.max(-W/2+mx/2,Math.min(W/2-mx/2,d.x)); d.y=Math.max(-H/2+mx/2,Math.min(H/2-mx/2,d.y)); });
    draw(); fit();
  }
  // ---------- filters and selection ----------
  const visible=n=>n.center||on[n.cat];
  function applyFilter(){ nodeSel.style('display',d=>visible(d)?null:'none'); linkSel.style('display',d=>visible(d.source)&&visible(d.target)?null:'none'); }
  const info=document.getElementById('info'), sheet=document.getElementById('sheet'), tab=document.getElementById('tab'); let selected=null;
  const setOpen=o=>{ sheet.classList.toggle('closed',!o); tab.textContent='Info '+(o?'×':'+'); tab.setAttribute('aria-expanded',String(o)); };
  tab.onclick=()=>setOpen(sheet.classList.contains('closed'));
  const row=(k,v)=>`<div class="row"><div>${k}</div><div>${v}</div></div>`, full=v=>`<div class="row full"><div>${v}</div></div>`;
  const dot=c=>`<span class="dot" style="background:${c}"></span>`;
  function record(){
    const srcs=inst.u.map(u=>`<a class="pill sm" href="${esc(u)}" target="_blank" rel="noopener">${esc(host(u))}</a>`).join('');
    info.innerHTML=full('<span class="ttl">'+esc(inst.n)+'</span>')+row('Location',esc(inst.c))+row('Tier',esc(TIER[inst.t]||inst.t)+(inst.tn?' · '+esc(inst.tn):''))
      +(inst.f?row('Funding',esc(inst.f)):row('Funding','The record does not state funding.'))+(inst.w?row('Watch',esc(inst.w)):'')
      +(inst.fl.length?row('Flags',inst.fl.map(esc).join(', ')+(inst.why?'<br>'+esc(inst.why):'')):'')
      +(srcs?row('Sources',srcs):'')+(inst.web?row('Website',`<a class="pill sm" href="${esc(inst.web)}" target="_blank" rel="noopener">${esc(host(inst.web))}</a>`):'')
      +`<div class="note">Circles are read from the record's funding text and flag fields, so a name can be split or grouped wrongly. The record text above is the authority.</div>`;
  }
  function select(n){
    selected=n;
    if(!n||n.center){ nodeSel.attr('opacity',1); linkSel.attr('opacity',1); nodeSel.select('text.lbl').attr('display',n?null:'none'); record(); if(n) setOpen(true); return; }
    const near=new Set([n.id,'c']); links.forEach(l=>{ if(l.source.id===n.id) near.add(l.target.id); if(l.target.id===n.id) near.add(l.source.id); });
    nodeSel.attr('opacity',d=>near.has(d.id)?1:.2); linkSel.attr('opacity',l=>(l.source.id===n.id||l.target.id===n.id)?1:.12); nodeSel.select('text.lbl').attr('display',d=>(d.id===n.id||(l=>false)(d))?null:'none');
    nodeSel.filter(d=>d.id===n.id||d.center).select('text.lbl').attr('display',null);
    const my=links.filter(l=>l.source.id===n.id||l.target.id===n.id);
    const conns=my.map(l=>{ const o=l.source.id===n.id?l.target:l.source; return `<span class="e"><button class="pill sm" style="border-color:${colOf(o)}" data-go="${o.id}">${dot(colOf(o))}${esc(o.label)}</button> ${esc(l.label)}</span>`; }).join('');
    info.innerHTML=full('<span class="ttl">'+esc(n.label)+'</span>')+row('Category',dot(CAT[n.cat].color)+esc(CAT[n.cat].label))+(n.note?row(n.cat==='link'?'Location':'Note',esc(n.note)):'')+row('Ties',String(my.length))+row('Connections',conns)
      +(n.go?row('Map',`<button class="pill sm" data-open="${esc(n.go)}">Open this space</button>`):'');
    info.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>select(byId[b.dataset.go]));
    info.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>openSpace(b.dataset.open));
    info.scrollTop=0; setOpen(true);
  }
  nodeSel.on('click',(e,d)=>{ e.stopPropagation(); select(selected&&selected.id===d.id?null:d); }).on('keydown',(e,d)=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); select(d); } });
  svg.on('click',()=>{ if(orbMoved>5){ orbMoved=0; return; } select(null); });
  bindOrbit(svg); REDRAW=draw; SWAYNODES=()=>N; SWAYLINKS=()=>links; startSpin();
  // category pills (only the groups this map has)
  const present=CATS.filter(c=>N.some(n=>n.cat===c));
  const catsEl=document.getElementById('cats');
  function renderCats(){
    catsEl.innerHTML=present.map(c=>{ const k=CAT[c], st=on[c]?`background:#000;border-color:${k.color};color:${k.color}`:`background:#000;border-color:#525252;color:#6f6f6f`; return `<button class="pill${on[c]?' on':''}" style="${st}" data-cat="${c}" aria-pressed="${on[c]}">${k.label} ${on[c]?'×':'+'}</button>`; }).join('');
    catsEl.querySelectorAll('button').forEach(b=>b.onclick=()=>{ on[b.dataset.cat]=!on[b.dataset.cat]; applyFilter(); renderCats(); });
  }
  renderCats(); applyFilter();
  const emp=document.getElementById('empty');
  emp.hidden=N.length>1; emp.textContent=N.length>1?'':'The record names no funder, flag or tie to draw.';
  setOpen(false); select(null);
  document.getElementById('zin').onclick=()=>svg.transition().call(zoom.scaleBy,1.3);
  document.getElementById('zout').onclick=()=>svg.transition().call(zoom.scaleBy,1/1.3);
  document.getElementById('zfit').onclick=()=>{ select(null); DOLLY=0; REDRAW&&REDRAW(); fit(true); };
  relayout();
  window.__nw=svg.node().clientWidth<700;
  cur={relayout,fit:()=>fit(),stop:()=>{ sim.stop(); cancelAnimationFrame(anim); }};
}
// ---------- spaces list ----------
const b1=document.getElementById('b1'), b2=document.getElementById('b2'), d1=document.getElementById('d1'), d2=document.getElementById('d2'), q=document.getElementById('q'), listEl=document.getElementById('list'), tiersEl=document.getElementById('tiers');
function drops(w){ d1.hidden=(w!==1); d2.hidden=(w!==2); b1.setAttribute('aria-expanded',String(w===1)); b2.setAttribute('aria-expanded',String(w===2)); setB2(w===2); if(w===2){ q.focus(); } }
let curRec=null; const setB2=open=>{ b2.textContent=(curRec?curRec.n+' · '+curRec.c:'Spaces')+' '+(open?'↑':'↓'); };
b1.onclick=()=>drops(d1.hidden?1:0); b2.onclick=()=>drops(d2.hidden?2:0);
const tierOn={A:true,B:true,U:true};
function renderTiers(){ tiersEl.innerHTML=['A','B','U'].map(t=>`<button class="pill sm${tierOn[t]?' on':''}" data-t="${t}">${TIER[t]} ${D.filter(r=>r.t===t).length} ${tierOn[t]?'×':'+'}</button>`).join(''); tiersEl.querySelectorAll('button').forEach(b=>b.onclick=()=>{ tierOn[b.dataset.t]=!tierOn[b.dataset.t]; renderTiers(); renderList(); }); }
const hay=D.map(r=>(r.n+' '+r.c+' '+r.co+' '+r.f).toLowerCase());
function renderList(){
  const t=q.value.trim().toLowerCase(); let all=[];
  const wb=t?new RegExp('(^|[^a-z0-9])'+t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')):null;
  for(let i=0;i<D.length;i++){ const r=D[i]; if(!tierOn[r.t]) continue; let sc=0;
    if(t){ const nm=r.n.toLowerCase(); if(nm.startsWith(t)) sc=4; else if(wb.test(nm)) sc=3; else if(nm.includes(t)) sc=2; else if((r.c+' '+r.co).toLowerCase().includes(t)) sc=1.5; else if(wb.test(r.f.toLowerCase())) sc=1; else continue; }
    all.push([sc,i]); }
  if(t) all.sort((a,b)=>b[0]-a[0]||a[1]-b[1]);
  const total=all.length, rows=all.slice(0,150).map(x=>D[x[1]]);
  listEl.innerHTML=rows.map(r=>`<button data-id="${esc(r.id)}">${esc(r.n)}<small>${esc(r.c)} · ${esc(TIER[r.t])}${r.nodes.length?' · '+r.nodes.length+(r.nodes.length===1?' tie':' ties'):''}</small></button>`).join('')+(total>rows.length?`<p class="note" style="grid-column:1/-1">${total-rows.length} more. Type to narrow the list.</p>`:'')+(total===0?'<p class="note">No space matches.</p>':'');
  listEl.querySelectorAll('button').forEach(b=>b.onclick=()=>{ openSpace(b.dataset.id); drops(0); });
}
q.oninput=renderList;
function openSpace(id){ const r=byRec[id]; if(!r) return; curRec=r; try{ history.replaceState(null,'','#'+id); }catch(e){} document.title=r.n+' · Culture Atlas Money Maps'; setB2(false); render(r); }
if(!window.__ro&&window.ResizeObserver){ window.__ro=true; new ResizeObserver(()=>window.dispatchEvent(new Event('resize'))).observe(document.querySelector('#map')); }
window.addEventListener('resize',()=>{ if(window.__rz) return; window.__rz=true; requestAnimationFrame(()=>{ window.__rz=false; if(!cur) return; const nw=svg.node().clientWidth<700; if(nw!==window.__nw){ window.__nw=nw; cur.relayout(); } else cur.fit(); }); });
renderTiers(); renderList();
const start=byRec[decodeURIComponent(location.hash.slice(1))]||D.find(r=>/^MoMA \(/.test(r.n))||D[0];
openSpace(start.id);
}).catch(err=>{ const e=document.getElementById('empty'); if(e){ e.hidden=false; e.textContent='The map data could not be loaded.'; } console.error(err); });
