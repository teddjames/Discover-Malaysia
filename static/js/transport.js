document.addEventListener('DOMContentLoaded', () => {
  const compare = document.getElementById('compareTransport');
  const from = document.getElementById('transportFrom');
  const to = document.getElementById('transportTo');
  const results = document.querySelector('.transport-results');
  if (!compare || !from || !to || !results) return;
  const esc = v => String(v ?? '').replace(/[&<>"']/g,c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icons = {flight:'✈️',bus:'🚌',train:'🚆',cab:'🚕',car:'🚗',ferry:'⛴️','cable-car':'🚠'};
  function outside(links){return (links||[]).map(l=>`<a class="small-button" target="_blank" rel="noopener noreferrer" href="${esc(l.url)}">${esc(l.name)} ↗</a>`).join('');}
  function maps(a,b,m){return 'https://www.google.com/maps/dir/?'+new URLSearchParams({api:'1',origin:a+', Malaysia',destination:b+', Malaysia',travelmode:m});}
  function duration(m){if(m == null)return 'Confirm with operator';const n=Number(m);return n>=60?`${Math.floor(n/60)} hr ${n%60 ? n%60+' min' : ''}`:`${n} min`;}
  function price(low,high){if(low == null)return 'Confirm with operator';return low===high?'RM '+low:`RM ${low}–${high}`;}
  async function run(){
    const origin=from.value,destination=to.value;
    if(origin===destination){results.innerHTML='<div class="no-transport">Please choose two different destinations.</div>';return;}
    compare.disabled=true;compare.textContent='Finding options…';
    try{
      const res=await fetch('/api/transport?'+new URLSearchParams({origin,destination}));
      const d=await res.json();
      if(!res.ok)throw new Error(d.error||'Unable to load transport options.');
      let html=`<div class="transport-results-header"><div><span class="section-label">POSSIBLE WAYS TO TRAVEL</span><h3>${esc(origin)} → ${esc(destination)}</h3><p class="micro-note">Links lead to provider search or information pages, not pre-booked tickets.</p></div><span>${d.recommendations.length} options to check</span></div>`;
      if(d.recommendations.length){html+='<div class="transport-guides">'+d.recommendations.map(r=>`<article class="travel-option"><div class="travel-option-head"><span class="travel-option-icon">${icons[r.mode]||'↗'}</span><div><span class="section-label">${esc(r.mode.replace('-',' ').toUpperCase())}</span><h4>${esc(r.title)}</h4><small>${esc(r.availability)}</small></div></div><p>${esc(r.description)}</p><ol>${(r.legs||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ol><div class="provider-links">${outside(r.providers)}</div><p class="micro-note">${esc(r.note)}</p></article>`).join('')+'</div>';} else {html+='<div class="no-transport">No curated recommendations for this pair. Check a route provider for available connections.</div>';}
      if(d.routes && d.routes.length){html+='<div class="legacy-estimates"><p class="section-label">SAMPLE ESTIMATES IN OUR DATABASE</p><p class="micro-note">Historical illustrations only—not live fares or confirmed departures.</p>'+d.routes.map(r=>`<div class="estimate-row"><strong>${esc(r.transport_type)}</strong><span>${esc(duration(r.duration_minutes))}</span><span>${esc(price(r.min_price,r.max_price))}</span></div>`).join('')+'</div>';}
      html+=`<div class="transport-map-actions"><a class="outline-button" target="_blank" rel="noopener noreferrer" href="${esc(d.maps_driving||maps(origin,destination,'driving'))}">Road directions on Maps ↗</a><a class="outline-button" target="_blank" rel="noopener noreferrer" href="${esc(d.maps_transit||maps(origin,destination,'transit'))}">Public transport on Maps ↗</a></div><p class="disclaimer">${esc(d.disclaimer)}</p>`;
      results.innerHTML=html;
    }catch(e){results.innerHTML=`<div class="no-transport">${esc(e.message)}. Try another route.</div>`;}
    finally{compare.disabled=false;compare.textContent='Find travel options ↗';}
  }
  compare.addEventListener('click',run);
  if(new URLSearchParams(window.location.search).has('destination'))run();
});
