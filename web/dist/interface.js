/* Navigation and presentation only. The financial engine stays in calculator.js. */
'use strict';
(() => {
  const main = document.querySelector('main');
  const header = document.querySelector('header');
  const intro = document.querySelector('.intro');
  intro.innerHTML = '<div><p class="eyebrow">DIT SU-LÅN</p><h1 id="page-title" tabindex="-1">Mit overblik</h1><p id="page-description">Se, hvad dit lån betyder for dig. Prøv dine egne tal.</p></div><span class="local-badge">Beregning på din enhed</span>';
  header.querySelector('.beta').remove();
  header.querySelector('.source-link').remove();
  const nav = document.createElement('nav');
  nav.className = 'app-nav';
  nav.setAttribute('aria-label', 'Hovednavigation');
  const views = [
    ['overview', 'Mit overblik', 'Se, hvad dit lån betyder for dig. Prøv dine egne tal.', '◫'],
    ['compare', 'Sammenlign', 'Hvad sker der, hvis du ændrer dit lån?', '⇄'],
    ['learn', 'Forstå dit lån', 'Små forklaringer, så du kan træffe dit eget valg.', '?'],
    ['chat', 'Spørg Bo', 'Få en forklaring med hjælp fra AI.', '◇'],
    ['lab', 'ML-lab', 'Et åbent eksperiment med simulerede data.', '⌘']
  ];
  for (const [id, label, , icon] of views) {
    const link = document.createElement('a');
    link.href = '#' + id;
    link.dataset.view = id;
    link.innerHTML = `<span aria-hidden="true">${icon}</span><span>${label}</span>`;
    nav.append(link);
  }
  header.append(nav);
  const sideNote = document.createElement('p');
  sideNote.className = 'sidebar-note';
  sideNote.textContent = 'Et overblik, du kan forstå. En beregning, du kan undersøge.';
  header.append(sideNote);
  const workspace = document.querySelector('.workspace');
  workspace.id = 'overview';
  workspace.dataset.page = 'overview';
  for (const id of ['compare', 'learn', 'lab', 'chat']) {
    const panel = document.createElement('section');
    panel.id = id;
    panel.dataset.page = id;
    panel.hidden = true;
    main.insertBefore(panel, document.querySelector('footer'));
  }
  document.getElementById('compare').append(document.querySelector('.explore-panel'), document.querySelector('.plans-panel'));
  document.getElementById('learn').append(document.querySelector('.learning-panel'), document.querySelector('.sources'));
  document.getElementById('lab').append(document.querySelector('.lab-panel'));
  const results = document.getElementById('results');
  results.append(document.querySelector('.guide'));
  results.append(document.querySelector('.math-panel'));
  document.querySelector('.result-topline h2').textContent = 'Din forventede plan';
  document.querySelector('.result-topline .step').remove();
  document.querySelector('.controls .step').remove();
  document.getElementById('input-heading').textContent = 'Dit lån';
  const loanLabel = document.querySelector('label[for="loan"]');
  loanLabel.childNodes[0].textContent = 'Hvor meget vil du låne om måneden? ';
  document.querySelector('.guide .eyebrow').textContent = 'BO FORKLARER';
  const advanced = document.createElement('details');
  advanced.className = 'advanced-input';
  advanced.innerHTML = '<summary>Gæld og tilbagebetaling</summary><p class="hint">Har du allerede gæld, eller vil du ændre renten?</p>';
  const debtLabel = document.querySelector('label[for="debt"]');
  const debtInput = document.getElementById('debt');
  const debtHint = debtInput.nextElementSibling;
  const ratePair = document.getElementById('rate').closest('.field-pair');
  debtLabel.before(advanced);
  advanced.append(debtLabel, debtInput, debtHint, ratePair);
  const form = document.getElementById('calculator');
  form.querySelector('.primary').innerHTML = 'Opdater min plan <span aria-hidden="true">→</span>';
  form.addEventListener('invalid', event => {
    let parent = event.target.parentElement;
    while (parent && parent !== form) {
      if (parent.tagName === 'DETAILS') parent.open = true;
      parent = parent.parentElement;
    }
  }, true);
  const dirty = document.getElementById('dirty');
  dirty.setAttribute('role', 'status');
  dirty.textContent = 'Du har ændringer, som ikke er beregnet endnu.';
  results.prepend(dirty);
  const feedback = document.createElement('p');
  feedback.id = 'update-feedback';
  feedback.className = 'sr-only';
  feedback.setAttribute('role', 'status');
  results.prepend(feedback);
  document.addEventListener('su:calculated', () => {
    feedback.textContent = 'Planen er opdateret. Gæld ved studieslut: ' + document.getElementById('total').textContent;
  });
  const mobileResult = document.createElement('a');
  mobileResult.className = 'mobile-result-link';
  mobileResult.href = '#results';
  mobileResult.textContent = 'Se resultatet ↓';
  form.querySelector('.primary').after(mobileResult);
  function navigate() {
    const hash = location.hash.slice(1);
    const fallback = hash === 'sources' ? 'learn' : hash === 'page-title' ? (nav.querySelector('[aria-current]')?.dataset.view || 'overview') : 'overview';
    const selected = views.find(v => v[0] === hash) || views.find(v => v[0] === fallback);
    document.querySelectorAll('[data-page]').forEach(page => { page.hidden = page.dataset.page !== selected[0]; });
    nav.querySelectorAll('a').forEach(link => {
      if (link.dataset.view === selected[0]) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    document.getElementById('page-title').textContent = selected[1];
    document.getElementById('page-description').textContent = selected[2];
    if (views.some(v => v[0] === hash)) window.scrollTo({top: 0, behavior: 'instant'});
  }
  window.addEventListener('hashchange', navigate);
  navigate();
})();
