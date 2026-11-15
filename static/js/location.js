// Geolocation only runs after a visitor actively clicks "Use my location".
// Latitude/longitude are submitted in a GET search; they can appear in URL history
// and web-server access logs. No permanent SQLite storage is performed.
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-geo-form]').forEach(form=>{
    const button=form.querySelector('[data-use-location]');
    const lat=form.querySelector('[data-lat]'),lon=form.querySelector('[data-lon]');
    const near=form.querySelector('[data-near-select]');
    const message=form.querySelector('[data-geo-feedback]');
    if(!button||!lat||!lon)return;
    near?.addEventListener('change',()=>{lat.value='';lon.value='';message.textContent='Using your selected city centre. Press Find places to search.'});
    button.addEventListener('click',()=>{
      if(!navigator.geolocation){message.textContent='This browser does not support location. Select a city instead.';return}
      button.disabled=true;message.textContent='Requesting location permission…';
      navigator.geolocation.getCurrentPosition(position=>{
        lat.value=position.coords.latitude.toFixed(6);
        lon.value=position.coords.longitude.toFixed(6);
        if(near)near.value='';
        button.disabled=false;
        message.textContent='Location received. Searching within your selected radius…';
        form.requestSubmit();
      },err=>{
        button.disabled=false;
        message.textContent=err.code===1?'Location permission declined. You can select any city manually.':'Unable to locate you. Try manually selecting a city.';
      },{enableHighAccuracy:false,timeout:12000,maximumAge:90000});
    });
  });
});
