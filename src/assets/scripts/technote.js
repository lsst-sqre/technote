/*
 * Support a configurable colour theme.
 *
 * This script is based on pydata-sphinx-theme:
 * https://github.com/pydata/pydata-sphinx-theme
 */

var prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

/**
 * Set the the body theme to the one specified by the user's browser/system
 * settings.
 *
 * @param {event} e
 */
function handleAutoTheme(e) {
  document.documentElement.dataset.theme = prefersDark.matches
    ? 'dark'
    : 'light';
}

/**
 * Set the theme using the specified mode.
 *
 * @param {str} mode - The theme mode to set. One of ["auto", "dark", "light"]
 */
function setTheme(mode) {
  if (mode !== 'light' && mode !== 'dark' && mode !== 'auto') {
    console.error(`Got invalid theme mode: ${mode}. Resetting to auto.`);
    mode = 'auto';
  }

  var colorScheme = prefersDark.matches ? 'dark' : 'light';
  document.documentElement.dataset.mode = mode;
  var theme = mode == 'auto' ? colorScheme : mode;

  // save mode and theme
  localStorage.setItem('mode', mode);
  localStorage.setItem('theme', theme);
  console.log(`[Technote]: Changed to ${mode} mode using the ${theme} theme.`);

  // add a listener if set on auto
  prefersDark.onchange = mode == 'auto' ? handleAutoTheme : '';
}

/**
 * add the theme listener on the btns of the navbar
 */
function addThemeModeListener() {
  // the theme was set a first time using the initial mini-script
  // running setMode will ensure the use of the dark mode if auto is selected
  setTheme(document.documentElement.dataset.mode);

  // Attach event handlers for toggling themes colors
  // document.querySelectorAll(".theme-switch-button").forEach((el) => {
  //   el.addEventListener("click", cycleMode);
  // });
}

/**
 * Execute a method if DOM has finished loading
 *
 * @param {function} callback the method to execute
 */
export function documentReady(callback) {
  if (document.readyState != 'loading') callback();
  else document.addEventListener('DOMContentLoaded', callback);
}

/**
 * Add handlers.
 */
documentReady(addThemeModeListener);

/**
 * Add listener for contents outline navigation button.
 */
function toggleContentsOutline() {
  document
    .querySelector('#technote-contents-toggle')
    .classList.toggle('technote-contents-toggle--active');
  document
    .querySelector('.technote-outline-container')
    .classList.toggle('technote-outline-container--visible');
}

documentReady(function () {
  document
    .querySelector('#technote-contents-toggle')
    .addEventListener('click', toggleContentsOutline);

  document.querySelectorAll('.technote-outline-container a').forEach((el) => {
    el.addEventListener('click', toggleContentsOutline);
  });
  console.log(
    '[Technote]: Added listener for contents outline navigation button.'
  );
});
