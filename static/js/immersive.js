/* Discover Malaysia immersive experience
   Pure browser Canvas 2D with projected geographic polygons, no external 3D library.
   Decorative tilt, scroll and globe effects respect reduced-motion preferences. */
(() => {
  'use strict';
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(pointer:fine)').matches;
  const nav = document.querySelector('.navbar');
  if (nav) {
    const setNav = () => nav.classList.toggle('scrolled', window.scrollY > 32);
    setNav(); window.addEventListener('scroll', setNav, {passive:true});
  }
  if ('IntersectionObserver' in window && !reduceMotion) {
    document.documentElement.classList.add('js-enhanced');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {entry.target.classList.add('in-view'); observer.unobserve(entry.target);}
      });
    }, {rootMargin:'0px 0px 55px 0px',threshold:.09});
    document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el));
  }

  // Tilt only on devices with a genuine mouse, never on touchscreen or reduced motion.
  if (finePointer && !reduceMotion) {
    document.querySelectorAll('.depth-tilt, .destination-card, .guide-item, .travel-option, .attraction-card, .hotel-card').forEach(card => {
      let frame = 0;
      const move = e => {
        if(frame) cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => {
          const r=card.getBoundingClientRect();
          const x=(e.clientX-r.left)/r.width-.5, y=(e.clientY-r.top)/r.height-.5;
          card.style.setProperty('--tilt-x',(-y*6).toFixed(2)+'deg');
          card.style.setProperty('--tilt-y',(x*6).toFixed(2)+'deg');
          card.style.setProperty('--hover-y','-5px');
        });
      };
      card.addEventListener('pointermove',move,{passive:true});
      card.addEventListener('pointerleave',()=>{
        if(frame) cancelAnimationFrame(frame);
        card.style.setProperty('--tilt-x','0deg');
        card.style.setProperty('--tilt-y','0deg');
        card.style.setProperty('--hover-y','0px');
      });
    });
  }

  const control = document.querySelectorAll('[data-destination-filter]');
  const cards = document.querySelectorAll('#homeDestinationGrid .immersive-destination-card');
  if (control.length && cards.length) {
    control.forEach(button => button.addEventListener('click', () => {
      const group = button.dataset.destinationFilter;
      control.forEach(b => {const active=b===button;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
      cards.forEach(card => {(card.closest('[data-card-shell]')||card).hidden = group!=='all' && card.dataset.category !== group;});
    }));
  }

  const canvas=document.getElementById('malaysiaGlobe');
  const stage=document.getElementById('globeStage');
  if (!canvas||!stage||!canvas.getContext) return;
  const ctx=canvas.getContext('2d',{alpha:true});
  if (!ctx) return;
  const rad=Math.PI/180;
  const sites=[
    {slug:'kuala-lumpur',name:'Kuala Lumpur',lat:3.139,lon:101.687,description:'A capital full of energy and contrasts'},
    {slug:'penang',name:'Penang',lat:5.414,lon:100.329,description:'Heritage streets, incredible food and sea views'},
    {slug:'langkawi',name:'Langkawi',lat:6.35,lon:99.8,description:'Tropical islands and extraordinary landscapes'},
    {slug:'kota-kinabalu',name:'Kota Kinabalu',lat:5.98,lon:116.073,description:'A gateway to Sabah’s coastal wonders'},
    {slug:'kuching',name:'Kuching',lat:1.553,lon:110.359,description:'Culture and discovery along the Sarawak River'}
  ];
  const urlMap=new Map();
  document.querySelectorAll('[data-globe-target]').forEach(a=>urlMap.set(a.dataset.globeTarget,a.href));
  sites.forEach(s=>{s.url=urlMap.get(s.slug)||'/explore?q='+encodeURIComponent(s.name);});
  const infoName=document.getElementById('globeFeatureName');
  const infoText=document.getElementById('globeFeatureSubtitle');
  const infoLink=document.getElementById('globeFeatureLink');
  const infoLabel=document.querySelector('.globe-card-label');
  let active=sites[0], features=[], shapeWidth=0, shapeHeight=0, dpr=1;
  let yaw=0, pitch=-.07, targetYaw=0, targetPitch=-.07;
  let dragging=false, moved=false, pointerStart=null, hovered=null;
  let pointerActiveUntil=0, lastFrame=0, pauseAnimation=false, canvasMarkers=[];
  let globeVisible=true;
  const setSite = site => {
    if(!site)return;
    active=site;
    if(infoName)infoName.textContent=site.name;
    if(infoText)infoText.textContent=site.description;
    if(infoLink)infoLink.href=site.url;
    if(infoLabel)infoLabel.textContent='FEATURED DESTINATION · '+String(sites.indexOf(site)+1).padStart(2,'0')+' / 05';
    document.querySelectorAll('[data-globe-target]').forEach(a=>a.classList.toggle('active',a.dataset.globeTarget===site.slug));
  };
  setSite(active);
  const wrapAngle = a => Math.atan2(Math.sin(a),Math.cos(a));
  const centreOn = site => {
    setSite(site);
    // Current rotation need not spin the globe more than half a turn.
    const desired=-(site.lon-102)*rad;
    targetYaw=yaw+wrapAngle(desired-yaw);
    targetPitch=-site.lat*rad;
    pointerActiveUntil=performance.now()+9000;
    if (reduceMotion) {yaw=targetYaw;pitch=targetPitch;draw();}
  };
  document.querySelectorAll('[data-globe-target]').forEach(a => {
    a.addEventListener('mouseenter',()=>centreOn(sites.find(s=>s.slug===a.dataset.globeTarget)));
    a.addEventListener('focus',()=>centreOn(sites.find(s=>s.slug===a.dataset.globeTarget)));
  });
  document.getElementById('globeReset')?.addEventListener('click', () => centreOn(sites[0]));
  function resize() {
    const rect=stage.getBoundingClientRect();
    shapeWidth=Math.max(230,rect.width);shapeHeight=shapeWidth;
    dpr=Math.min(2, window.devicePixelRatio||1);
    canvas.width=Math.round(shapeWidth*dpr);canvas.height=Math.round(shapeHeight*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    draw();
  }
  const size=()=>({cx:shapeWidth/2,cy:shapeHeight*.49,r:shapeWidth*.365});
  function sphere(lat,lon){
    const la=lat*rad,lo=(lon-102)*rad+yaw;
    const x=Math.cos(la)*Math.sin(lo),y=-Math.sin(la),z=Math.cos(la)*Math.cos(lo);
    const co=Math.cos(pitch),si=Math.sin(pitch);
    return {x,y:y*co-z*si,z:y*si+z*co};
  }
  function project(v){const {cx,cy,r}=size();return {x:cx+v.x*r,y:cy+v.y*r,z:v.z};}
  function clipPolygon(vertices){const out=[],threshold=.001;
    for(let i=0;i<vertices.length;i++){
      const a=vertices[i],b=vertices[(i+1)%vertices.length],af=a.z>=threshold,bf=b.z>=threshold;
      if(af)out.push(a);
      if(af!==bf){let t=(threshold-a.z)/(b.z-a.z);out.push({x:a.x+t*(b.x-a.x),y:a.y+t*(b.y-a.y),z:threshold});}
    }return out;
  }
  function polyPath(points){if(points.length<3)return false;ctx.beginPath();points.forEach((v,i)=>{const pt=project(v);if(i===0)ctx.moveTo(pt.x,pt.y);else ctx.lineTo(pt.x,pt.y)});ctx.closePath();return true;}
  function drawGeoLine(points,color,width,alpha){ctx.beginPath();let prev=null,started=false;const threshold=.002;
    for(const pt of points){const v=sphere(pt[1],pt[0]);if(prev){const a=prev,b=v,fa=a.z>threshold,fb=b.z>threshold;
        if(fa&&fb){const av=project(a),bv=project(b);if(!started){ctx.moveTo(av.x,av.y);started=true;}ctx.lineTo(bv.x,bv.y)}
        else if(fa!==fb){const t=(threshold-a.z)/(b.z-a.z),hit={x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t,z:threshold},h=project(hit);
          if(fa){if(!started){const aa=project(a);ctx.moveTo(aa.x,aa.y);}ctx.lineTo(h.x,h.y);}else {ctx.moveTo(h.x,h.y);const bb=project(b);ctx.lineTo(bb.x,bb.y);}
          started=fb;
        }else started=false;
      }prev=v;
    }
    ctx.globalAlpha=alpha;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();ctx.globalAlpha=1;
  }
  function draw(){if(!shapeWidth)return;
    const {cx,cy,r}=size();ctx.clearRect(0,0,shapeWidth,shapeHeight);
    // Atmospheric halo + small distant stars.
    let halo=ctx.createRadialGradient(cx,cy,r*.72,cx,cy,r*1.3);halo.addColorStop(0,'#35e49a19');halo.addColorStop(.7,'#36d08b15');halo.addColorStop(1,'#35e49a00');ctx.fillStyle=halo;ctx.fillRect(cx-r*1.4,cy-r*1.4,r*2.8,r*2.8);
    const sea=ctx.createRadialGradient(cx-r*.35,cy-r*.42,r*.05,cx+r*.21,cy+r*.22,r*1.45);
    sea.addColorStop(0,'#224f45');sea.addColorStop(.33,'#11362d');sea.addColorStop(.76,'#0b2825');sea.addColorStop(1,'#061b18');
    ctx.save();ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.clip();ctx.fillStyle=sea;ctx.fillRect(cx-r,cy-r,r*2,r*2);
    // Graticule projected onto the sphere.
    for(let lat=-75;lat<=75;lat+=15){const pts=[];for(let lon=-180;lon<=180;lon+=3)pts.push([lon,lat]);drawGeoLine(pts,'#74c9a0',.65,.13)}
    for(let lon=-180;lon<180;lon+=15){const pts=[];for(let lat=-88;lat<=88;lat+=3)pts.push([lon,lat]);drawGeoLine(pts,'#74c9a0',.65,.12)}
    for(const f of features){const malaysia=f.n==='Malaysia';for(const ring of f.p){const pts=clipPolygon(ring.map(q=>sphere(q[1],q[0])));
      if(!polyPath(pts))continue;
      ctx.fillStyle=malaysia?'#4cce88':'#3e8a69';ctx.globalAlpha=malaysia?.92:.46;ctx.fill();
      ctx.strokeStyle=malaysia?'#cbffe0':'#9cd8b3';ctx.globalAlpha=malaysia?.92:.33;ctx.lineWidth=malaysia?1.6:.56;ctx.stroke();ctx.globalAlpha=1;
    }}
    // Subtle depth shading and atmospheric rim.
    const shade=ctx.createRadialGradient(cx-r*.28,cy-r*.33,r*.03,cx+r*.24,cy+r*.08,r*1.3);
    shade.addColorStop(0,'#85edb900');shade.addColorStop(.55,'#06151200');shade.addColorStop(.85,'#0416126b');shade.addColorStop(1,'#03120eae');ctx.fillStyle=shade;ctx.fillRect(cx-r,cy-r,2*r,2*r);
    ctx.restore();ctx.beginPath();ctx.arc(cx,cy,r,0,2*Math.PI);ctx.strokeStyle='#87e9b54a';ctx.lineWidth=1.4;ctx.stroke();
    ctx.save();ctx.shadowColor='#67edae';ctx.shadowBlur=16;ctx.beginPath();ctx.arc(cx,cy,r*.995,-.35,1.3);ctx.strokeStyle='#bafbd17a';ctx.lineWidth=2;ctx.stroke();ctx.restore();
    canvasMarkers=[];
    for(const s of sites){const v=sphere(s.lat,s.lon);if(v.z<.05)continue;const pp=project(v),isActive=s.slug===active.slug;
      canvasMarkers.push({...pp,site:s});
      ctx.save();ctx.shadowColor=isActive?'#adffe1':'#58e5aa';ctx.shadowBlur=isActive?23:12;
      ctx.beginPath();ctx.arc(pp.x,pp.y,isActive?7:4.2,0,Math.PI*2);ctx.fillStyle=isActive?'#edfff3':'#96efbe';ctx.fill();ctx.restore();
      ctx.beginPath();ctx.arc(pp.x,pp.y,isActive?15:9,0,Math.PI*2);ctx.strokeStyle=isActive?'#bfffd0a3':'#bdfad366';ctx.lineWidth=isActive?1.5:1;ctx.stroke();
      if(isActive){ctx.beginPath();ctx.moveTo(pp.x+9,pp.y-9);ctx.lineTo(pp.x+36,pp.y-37);ctx.lineTo(pp.x+92,pp.y-37);ctx.strokeStyle='#a0f7c8c9';ctx.lineWidth=1;ctx.stroke();ctx.font='600 10px "DM Sans",Arial';ctx.fillStyle='#ddffe8';ctx.fillText(s.name,pp.x+39,pp.y-43);}
    }
  }
  let rafId=null;
  function animate(t){if(!globeVisible||document.hidden){rafId=null;return;}
    if(lastFrame===0)lastFrame=t;
    const dt=Math.min(100,t-lastFrame);lastFrame=t;
    if(!reduceMotion&&!dragging&&t>pointerActiveUntil){targetYaw+=dt*.000038;targetPitch= -.07+Math.sin(t*.00019)*.028;}
    yaw+=wrapAngle(targetYaw-yaw)*Math.min(1,dt*.007);
    pitch+=(targetPitch-pitch)*Math.min(1,dt*.007);
    draw();rafId=requestAnimationFrame(animate);
  }
  function start(){if(rafId===null&&!reduceMotion&&!document.hidden&&globeVisible){lastFrame=0;rafId=requestAnimationFrame(animate)}else if(reduceMotion)draw()}
  if('IntersectionObserver' in window){new IntersectionObserver(entries=>{globeVisible=entries[0].isIntersecting;if(globeVisible)start();},{threshold:0}).observe(stage)}
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)start()});
  const findMarker=e=>{const r=canvas.getBoundingClientRect(),mx=(e.clientX-r.left)*(shapeWidth/r.width),my=(e.clientY-r.top)*(shapeHeight/r.height);return canvasMarkers.map(p=>({...p,d:Math.hypot(p.x-mx,p.y-my)})).filter(p=>p.d<20).sort((a,b)=>a.d-b.d)[0]};
  const onDown=e=>{if(e.button!==0)return;pointerStart={x:e.clientX,y:e.clientY};dragging=true;moved=false;stage.classList.add('dragging');pointerActiveUntil=performance.now()+7000;canvas.setPointerCapture?.(e.pointerId)};
  const onMove=e=>{const marker=findMarker(e);
    canvas.style.cursor=marker&&!dragging?'pointer':'';
    if(!dragging||!pointerStart)return;
    const dx=e.clientX-pointerStart.x,dy=e.clientY-pointerStart.y;
    if(Math.abs(dx)>2||Math.abs(dy)>2)moved=true;
    targetYaw+=dx*.007;targetPitch=Math.max(-1.2,Math.min(1.2,targetPitch+dy*.005));
    pointerStart={x:e.clientX,y:e.clientY};pointerActiveUntil=performance.now()+10000;
    if(reduceMotion){yaw=targetYaw;pitch=targetPitch;draw();}
  };
  const onUp=e=>{if(!dragging)return;dragging=false;stage.classList.remove('dragging');if(!moved){const marker=findMarker(e);if(marker){window.location.assign(marker.site.url);}}pointerStart=null;};
  canvas.addEventListener('pointerdown',onDown);canvas.addEventListener('pointermove',onMove,{passive:true});canvas.addEventListener('pointerup',onUp);canvas.addEventListener('pointercancel',()=>{dragging=false;pointerStart=null;stage.classList.remove('dragging')});
  window.addEventListener('resize',resize,{passive:true});
  new ResizeObserver(resize).observe(stage);
  resize();start();
  const worldUrl=canvas.dataset.worldUrl;
  if(worldUrl){fetch(worldUrl).then(r=>{if(!r.ok)throw new Error('World shapes not loaded');return r.json()}).then(data=>{if(Array.isArray(data.features))features=data.features;draw()}).catch(()=>{ /* A stylised grid globe is a graceful offline fallback. */ });}
})();
