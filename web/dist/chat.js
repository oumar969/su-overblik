'use strict';
(() => {
  const launcher = document.createElement('button');
  launcher.type = 'button'; launcher.className = 'chat-launcher';
  launcher.setAttribute('aria-controls', 'bo-chat-window');
  launcher.setAttribute('aria-expanded', 'false');
  launcher.innerHTML = '<img src="guide.png" width="40" height="40" alt=""><span>Spørg Bo</span>';
  const page = document.createElement('section');
  page.id = 'bo-chat-window'; page.className = 'chat-window'; page.hidden = true;
  page.setAttribute('role', 'dialog'); page.setAttribute('aria-labelledby', 'bo-chat-title');
  document.body.append(launcher, page);
  page.innerHTML = `<div class="bo-chat"><div class="chat-title"><img src="guide.png" width="48" height="48" alt=""><div><h2 id="bo-chat-title">Spørg Bo</h2><p>Din AI-hjælper til SU-lån</p></div><button type="button" id="close-bo-chat" aria-label="Luk chatten">×</button></div>
  <p class="hint">AI kan tage fejl. Kontrollér vigtige oplysninger hos SU.dk og Borger.dk. Chatten har ikke live adgang til reglerne.</p>
  <div id="chat-messages" role="log" aria-label="Samtale med Bo" aria-live="polite"></div>
  <form id="bo-form"><label for="bo-question">Dit spørgsmål</label><textarea id="bo-question" rows="3" maxlength="1200" required placeholder="Hvorfor vokser gælden efter studiet?"></textarea>
  <label class="chat-consent"><input id="share-plan" type="checkbox">Del min senest beregnede låneplan med Bo</label>
  <p class="hint">Beskeder behandles af Vercel og Groq. Skriv ikke CPR eller følsomme oplysninger.</p><details class="chat-privacy"><summary>Om dine data</summary><p class="hint">De seneste beskeder medsendes. Din låneplan sendes kun, hvis du vælger det. Budgetindtægter og udgifter medsendes ikke.</p></details>
  <div class="chat-actions"><button class="primary" type="submit">Send til Bo</button><button id="clear-chat" type="button">Ryd samtale</button></div><p id="chat-status" role="status"></p></form></div>`;
  const form = document.getElementById('bo-form'), question = document.getElementById('bo-question');
  const status = document.getElementById('chat-status'), log = document.getElementById('chat-messages');
  const send = form.querySelector('[type=submit]'), clear = document.getElementById('clear-chat');
  let messages = [];
  function toggle(open) {
    page.hidden = !open;
    launcher.setAttribute('aria-expanded', String(open));
    if (open) question.focus({preventScroll: true});
    else launcher.focus({preventScroll: true});
  }
  launcher.addEventListener('click', () => toggle(page.hidden));
  document.getElementById('close-bo-chat').addEventListener('click', () => toggle(false));
  page.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); toggle(false); }
  });
  function openFromLink() { if (location.hash === '#chat') toggle(true); }
  window.addEventListener('hashchange', openFromLink);
  openFromLink();
  function bubble(role, content) {
    const item = document.createElement('p'); item.className = 'chat-message ' + role;
    const label = document.createElement('strong'); label.textContent = role === 'user' ? 'Dig' : 'Bo';
    const text = document.createElement('span'); text.textContent = content;
    item.append(label, text); log.append(item);
    log.scrollTop = log.scrollHeight;
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const content = question.value.trim(); if (!content || send.disabled) return;
    send.disabled = clear.disabled = true; status.textContent = 'Bo tænker…';
    const next = [...messages.slice(-6), {role: 'user', content}];
    const body = {messages: next};
    if (document.getElementById('share-plan').checked) {
      body.plan = {};
      for (const key of ['loan','debt','start','end','rate','interval']) body.plan[key] = current.input[key];
    }
    try {
      const response = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body), signal: AbortSignal.timeout(30000)});
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw Error(data.error || 'Chatten kræver serveren på Vercel. Den er ikke tilgængelig i den statiske Docker-udgave.');
      if (typeof data.answer !== 'string') throw Error('Svaret kunne ikke læses.');
      bubble('user', content); bubble('assistant', data.answer);
      messages = [...next, {role: 'assistant', content: data.answer.slice(0,1200)}];
      question.value = ''; status.textContent = '';
    } catch (error) { status.textContent = error.name === 'TimeoutError' ? 'Svaret tog for lang tid. Prøv igen.' : error.message; }
    finally { send.disabled = clear.disabled = false; }
  });
  clear.addEventListener('click', () => { messages = []; log.replaceChildren(); status.textContent = 'Samtalen er ryddet her på siden. Dette sletter ikke eventuelle logs hos tjenesteudbyderne.'; });
})();
