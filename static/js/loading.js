
/* Discover Malaysia — Loading Screen */

(() => {
  'use strict';

  const loader =
    document.getElementById('discoverLoading');

  const message =
    document.getElementById('discoverLoadingMessage');

  if (!loader) return;

  let leaving = false;
  let safetyTimer;
  let fadeTimer;
  let initialTimer;

  const reduceMotion = () =>
    window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;

  function hideLoader() {
    window.clearTimeout(safetyTimer);

    if (loader.hidden || leaving) return;

    leaving = true;
    loader.classList.add('is-leaving');
    loader.setAttribute('aria-hidden', 'true');

    const finish = () => {
      loader.hidden = true;
      loader.classList.remove('is-leaving');
      leaving = false;
    };

    if (reduceMotion()) {
      finish();
    } else {
      fadeTimer = window.setTimeout(finish, 400);
    }
  }

  function showLoader(text) {
    window.clearTimeout(safetyTimer);
    window.clearTimeout(initialTimer);
    window.clearTimeout(fadeTimer);

    leaving = false;
    loader.hidden = false;

    loader.classList.remove('is-leaving');
    loader.removeAttribute('aria-hidden');

    if (message) {
      message.textContent =
        text || 'Taking you somewhere beautiful…';
    }

    safetyTimer = window.setTimeout(
      hideLoader,
      20000
    );
  }

  // Hide once the browser has finished loading.
  if (document.readyState === 'complete') {
    hideLoader();
  } else {
    window.addEventListener(
      'load',
      hideLoader,
      { once: true }
    );
  }

  // Fallback for slow external assets.
  initialTimer = window.setTimeout(
    hideLoader,
    5000
  );

  // Show loader for internal navigation.
  document.addEventListener('click', (event) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.ctrlKey ||
      event.metaKey ||
      event.altKey ||
      event.shiftKey
    ) {
      return;
    }

    const anchor =
      event.target.closest('a[href]');

    if (
      !anchor ||
      anchor.hasAttribute('download') ||
      (anchor.target && anchor.target !== '_self')
    ) {
      return;
    }

    let url;

    try {
      url = new URL(
        anchor.href,
        window.location.href
      );
    } catch {
      return;
    }

    if (
      !['http:', 'https:'].includes(url.protocol) ||
      url.origin !== window.location.origin
    ) {
      return;
    }

    if (
      url.pathname === window.location.pathname &&
      url.search === window.location.search &&
      (url.hash || anchor.getAttribute('href') === '#')
    ) {
      return;
    }

    showLoader('Taking you somewhere beautiful…');
  });

  // Show loader for internal form submissions.
  document.addEventListener('submit', (event) => {
    if (event.defaultPrevented) return;

    const form = event.target;

    if (
      !(form instanceof HTMLFormElement) ||
      !form.checkValidity() ||
      (form.target && form.target !== '_self')
    ) {
      return;
    }

    let url;

    try {
      url = new URL(
        form.action || window.location.href,
        window.location.href
      );
    } catch {
      return;
    }

    if (url.origin !== window.location.origin) {
      return;
    }

    showLoader('Finding your next destination…');
  });

  // Remove loader when returning via browser history.
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) hideLoader();
  });

  // Allow dismissing the loader.
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') hideLoader();
  });
})();
