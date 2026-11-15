document.addEventListener('DOMContentLoaded', () => {
  const start = document.getElementById('tripStartDate');
  const end = document.getElementById('tripEndDate');
  const summary = document.getElementById('tripLengthSummary');
  const submit = document.getElementById('generateTrip');
  const results = document.getElementById('itineraryResults');
  if(!start || !end || !summary || !submit || !results) return;
  const esc = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const formatDate = dateString => {const d=new Date(dateString+'T12:00:00');return new Intl.DateTimeFormat('en-MY',{weekday:'short',day:'numeric',month:'short',year:'numeric'}).format(d);};
  const pad = n => String(n).padStart(2,'0');
  const localISO = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  function dateSpan(){
    if(!start.value || !end.value) return null;
    const a=Date.parse(start.value+'T12:00:00Z'), b=Date.parse(end.value+'T12:00:00Z');
    if(!Number.isFinite(a)||!Number.isFinite(b))return null;
    return Math.round((b-a)/86400000)+1;
  }
  function updateDates(){
    if(start.value)end.min=start.value;
    const days=dateSpan();
    summary.textContent=!start.value || !end.value?'Choose both dates to calculate your stay.' : days<=0?'Departure cannot be before arrival.' : days>90?'For this version, choose a stay of 90 days or fewer.' : `${days} ${days===1?'day':'days'} · ${days-1} ${days-1===1?'night':'nights'} · ${formatDate(start.value)} to ${formatDate(end.value)}`;
  }
  // Native date inputs open the browser's familiar calendar picker.
  const today=new Date();
  start.min=localISO(today);
  start.value=localISO(today);
  const defaultEnd=new Date(today.getFullYear(),today.getMonth(),today.getDate()+3);
  end.min=start.value;
  end.value=localISO(defaultEnd);
  start.addEventListener('change',()=>{if(end.value<start.value)end.value=start.value;updateDates();});
  end.addEventListener('change',updateDates);
  updateDates();

  const allButtons=Array.from(document.querySelectorAll('.planner-option'));
  function chosen(type){return allButtons.filter(b=>b.dataset.type===type && b.classList.contains('selected'));}
  function updatePressed(){allButtons.forEach(b=>b.setAttribute('aria-pressed',b.classList.contains('selected')?'true':'false'));}
  allButtons.forEach(b=>b.addEventListener('click',()=>{
    const type=b.dataset.type;
    if(type==='budget'){
      allButtons.filter(x=>x.dataset.type==='budget').forEach(x=>x.classList.remove('selected'));
      b.classList.add('selected');
    }else if(type==='interest'){
      const anything=allButtons.find(x=>x.dataset.type==='interest'&&x.dataset.value==='anything');
      if(b.dataset.value==='anything'){
        allButtons.filter(x=>x.dataset.type==='interest').forEach(x=>x.classList.remove('selected'));
        b.classList.add('selected');
      }else{
        if(anything)anything.classList.remove('selected');
        b.classList.toggle('selected');
        if(!chosen('interest').length && anything)anything.classList.add('selected');
      }
    }else if(type==='destination')b.classList.toggle('selected');
    updatePressed();
  }));
  updatePressed();

  submit.addEventListener('click',async()=>{
    const days=dateSpan();
    if(!start.value||!end.value||!days||days<1||days>90){summary.focus?.();alert('Choose a valid arrival and departure date, up to 90 days apart.');return;}
    const budget=chosen('budget')[0]?.dataset.value;
    const interests=chosen('interest').map(b=>b.dataset.value);
    const destinations=chosen('destination').map(b=>b.dataset.value);
    if(!budget || !destinations.length){alert('Choose a budget and at least one destination.');return;}
    submit.disabled=true;submit.textContent='Building your itinerary…';
    results.innerHTML='<div class="planner-loading"><span class="section-label">YOUR ITINERARY</span><h2>Building your trip…</h2></div>';
    try{
      const response=await fetch('/api/trip-planner',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({start_date:start.value,end_date:end.value,budget,interests,destinations})});
      const data=await response.json();
      if(!response.ok)throw new Error(data.error||'Could not build your itinerary.');
      renderTrip(data);
    }catch(e){results.innerHTML=`<div class="planner-error"><h2>Couldn't build your trip.</h2><p>${esc(e.message)}</p></div>`;}
    finally{submit.disabled=false;submit.textContent='Build My Trip →';}
  });

  function renderTrip(data){
    if(!data.itinerary?.length){results.innerHTML='<div class="planner-empty">No itinerary activities available for these destinations yet.</div>';return;}
    let html=`<div class="itinerary-header"><span class="section-label">YOUR PERSONAL ITINERARY</span><h2>${esc(data.days)} days exploring Malaysia</h2><p>${esc(data.start_date?formatDate(data.start_date):'')} ${data.end_date?'– '+esc(formatDate(data.end_date)):''} · ${esc(data.nights)} nights · ${esc(data.budget)} budget</p><p>${data.interests.includes('anything')?'Every interest category is included.':'Selected interests: '+esc(data.interests.join(', ')||'Anything')}</p></div><div class="itinerary-days">`;
    for(const day of data.itinerary){
      html+=`<section class="itinerary-day"><div class="itinerary-day-header"><span>DAY ${esc(day.day)}</span><h3>${esc(day.destinations?.join(' + ') || 'Free exploration')}</h3>${day.date?`<span class="itinerary-date">${esc(formatDate(day.date))}</span>`:''}</div><div class="day-activities">`;
      if(!day.activities.length){html+='<p>Open day: explore at your own pace, rest, or add experiences manually. No additional activities are currently listed for this day.</p>';}
      day.activities.forEach((a,i)=>{
        const times=['09:00 AM','12:00 PM','03:00 PM','07:00 PM'];
        html+=`<article class="itinerary-activity"><div class="activity-time">${times[i]||'Later'}</div><div class="activity-content"><span class="activity-category">${esc(a.category)}</span><h4>${esc(a.name)}</h4><p>${esc(a.description)}</p><div class="activity-meta"><span>📍 ${esc(a.destination)}</span><span>⏱ ${esc(a.duration)}</span><span>⭐ ${a.rating==null?'Unrated':esc(a.rating)}</span><span>${a.price==null?'Price to check':'RM '+esc(a.price)}</span></div></div></article>`;
      });
      html+=`</div><div class="day-summary"><span>💰 Known listed activities: RM ${esc(day.total_cost)} (excludes unpriced activities, transport and accommodation)</span><span>📍 ${esc(day.destinations?.join(' • ')||'Flexible day')}</span></div></section>`;
    }
    html+='</div><p class="coverage-disclaimer inline-disclaimer">Itinerary activity times are suggestions, not confirmed opening hours. Budget levels guide your preferences; the displayed totals are not a guaranteed all-in trip budget. Travel time between destinations is not calculated.</p>';
    if(data.interest_fallback)html+='<p class="coverage-disclaimer inline-disclaimer">No activities matched your selected interest categories, so the guide included other available activities.</p>';
    results.innerHTML=html;
    results.scrollIntoView({behavior:'smooth',block:'start'});
  }
});
