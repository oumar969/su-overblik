'use strict';
(() => {
  const page = document.getElementById('chat');
  page.innerHTML = `<div class="bo-chat"><div class="chat-title"><img src="guide.png" width="70" height="70" alt=""><div><h2>Spørg Bo</h2><p>Få hjælp til at forstå dit SU-lån.</p></div></div>
  <p class="hint">AI kan tage fejl. Kontrollér vigtige oplysninger hos SU.dk og Borger.dk. Chatten har ikke live adgang til reglerne.</p>
  <div id="chat-messages" role="log" aria-label="Samtale med Bo" aria-live="polite"></div>
  <form id="bo-form"><label for="bo-question">Dit spørgsmål</label><textarea id="bo-question" rows="3" maxlength="1200" required placeholder="Hvorfor vokser gælden efter studiet?"></textarea>
  <label class="chat-consent"><input id="share-plan" type="checkbox">Del min senest beregnede låneplan med Bo</label>
  <p class="hint">Når du sender, behandles beskeden og de seneste beskeder af Vercel og Groq. Din låneplan sendes kun, hvis du vælger det. Budgetindtægter og udgifter medsendes ikke. Skriv ikke CPR eller andre følsomme oplysninger.</p>
  <div class="chat-actions"><button class="primary" type="submit">Send til Bo</button><button id="clear-chat" type="button">Ryd samtale</button></div><p id="chat-status" role="status"></p></form></div>`;
  const form = document.getElementById('bo-form'), question = document.getElementById('bo-question');
  const status = document.getElementById('chat-status'), log = document.getElementById('chat-messages');
  const send = form.querySelector('[type=submit]'), clear = document.getElementById('clear-chat');
  let messages = [];
  function bubble(role, content) {
    const item = document.createElement('p'); item.className = 'chat-message ' + role;
    const label = document.createElement('strong'); label.textContent = role === 'user' ? 'Dig' : 'Bo';
    const text = document.createElement('span'); text.textContent = content;
    item.append(label, text); log.append(item);
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
