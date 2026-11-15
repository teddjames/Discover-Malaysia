/* Image-led hero. Uses real bundled photos; only the active gallery tile changes. */
(() => {
  'use strict';
  const photo=document.getElementById('editorialHeroPhoto');
  if(!photo) return;
  const img=document.getElementById('editorialHeroImage');
  const name=document.getElementById('editorialHeroName');
  const subtitle=document.getElementById('editorialHeroDescription');
  const link=document.getElementById('editorialHeroLink');
  const counter=document.getElementById('heroSlideCounter');
  const slides=[
    ['kuala-lumpur','Kuala Lumpur','The energy of a vibrant capital.','Kuala Lumpur skyline at blue hour'],
    ['langkawi','Langkawi','The freedom of an island escape.','Langkawi coastal resort and turquoise sea'],
    ['batu-caves','Batu Caves','Where culture meets wonder.','Murugan statue at Batu Caves'],
    ['cameron-highlands','Cameron Highlands','Slow mornings above the clouds.','Rolling tea plantations of Cameron Highlands'],
    ['penang','Penang','Heritage, stories and the sea.','Temple architecture in Penang']
  ];
  let index=0;
  let swapping=false;
  function navigate(delta) {
    if(swapping) return;
    swapping=true;
    index=(index+delta+slides.length)%slides.length;
    const [slug,title,description,alt]=slides[index];
    const nextUrl=photo.dataset.imageBase+'/'+slug+'.webp';
    const preloader=new Image();
    preloader.onload=()=>{
      img.classList.add('is-changing');
      window.setTimeout(()=>{
        img.src=nextUrl;img.alt=alt;
        name.textContent=title;subtitle.textContent=description;
        link.href='/destinations/'+slug;link.setAttribute('aria-label','Explore '+title);
        counter.textContent=String(index+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');
        img.classList.remove('is-changing');swapping=false;
      }, window.matchMedia('(prefers-reduced-motion:reduce)').matches?0:160);
    };
    preloader.onerror=()=>{swapping=false};
    preloader.src=nextUrl;
  }
  document.getElementById('heroPrev')?.addEventListener('click',()=>navigate(-1));
  document.getElementById('heroNext')?.addEventListener('click',()=>navigate(1));
  // Native touch gesture for small screens. No wheel hijacking or autoplay.
  let touchX=null;
  photo.addEventListener('touchstart',e=>{touchX=e.changedTouches[0]?.screenX??null},{passive:true});
  photo.addEventListener('touchend',e=>{if(touchX===null)return;const diff=(e.changedTouches[0]?.screenX??touchX)-touchX;if(Math.abs(diff)>55)navigate(diff<0?1:-1);touchX=null},{passive:true});
  document.addEventListener('keydown',e=>{if(document.activeElement?.closest('.hero-photo-wrap')){if(e.key==='ArrowRight'){e.preventDefault();navigate(1)}if(e.key==='ArrowLeft'){e.preventDefault();navigate(-1)}}});
  // The cards have an optional, keyboard-accessible quick-view reverse side.
  document.querySelectorAll('[data-card-shell]').forEach(shell=>{
    const button=shell.querySelector('[data-card-peek]');
    const close=shell.querySelector('[data-card-close]');
    const reverse=shell.querySelector('.editorial-card-back');
    const face=shell.querySelector('.editorial-card');
    const setOpen=(open,restoreFocus=false)=>{
      shell.classList.toggle('is-peeking',open);
      button?.setAttribute('aria-expanded',String(open));
      reverse?.setAttribute('aria-hidden',String(!open));
      if(reverse)reverse.inert=!open;
      if(face)face.tabIndex=open?-1:0;
      if(restoreFocus)button?.focus();
      else if(open)close?.focus();
    };
    button?.addEventListener('click',()=>setOpen(true));
    close?.addEventListener('click',()=>setOpen(false,true));
    shell.addEventListener('keydown',e=>{if(e.key==='Escape'&&shell.classList.contains('is-peeking')){e.preventDefault();setOpen(false,true)}});
  });
})();
