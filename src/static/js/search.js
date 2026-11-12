(() => {
  'use strict';

  const form = document.getElementById('site-search-form');
  const input = document.getElementById('site-search-input');
  const status = document.getElementById('search-status');
  const results = document.getElementById('search-results');
  const suggestions = document.getElementById('search-suggestions');

  if (!form || !input || !status || !results) return;

  const normalize = (value) => String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase('es')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();

  const STOP_WORDS = new Set([
    'a', 'al', 'algo', 'como', 'con', 'cuando', 'de', 'del', 'donde', 'el', 'ella',
    'en', 'es', 'esa', 'ese', 'esta', 'este', 'he', 'la', 'las', 'le', 'lo', 'los',
    'me', 'mi', 'mis', 'mucho', 'no', 'o', 'para', 'pero', 'por', 'que', 'se', 'si',
    'sin', 'sobre', 'soy', 'su', 'sus', 'te', 'tengo', 'tu', 'un', 'una', 'uno', 'y',
    'quiero', 'necesito', 'creo', 'puedo', 'hacer', 'hago', 'ahora', 'han', 'hay'
  ]);

  const tokens = (value) => normalize(value).split(/\s+/)
    .filter((word) => word.length > 1 && !STOP_WORDS.has(word));

  const resultTemplate = document.getElementById('search-result-template');

  const createResult = (item) => {
    const link = resultTemplate.content.firstElementChild.cloneNode(true);
    link.href = item.url;
    link.querySelector('.search-result-type').textContent = item.type || 'Contenido';
    link.querySelector('h2').textContent = item.title;
    link.querySelector('p').textContent = item.description;
    return link;
  };

  const rankItem = (item, query, queryTokens) => {
    const title = normalize(item.title);
    const description = normalize(item.description);
    const keywords = normalize((item.keywords || []).join(' '));
    const type = normalize(item.type);
    const fields = [
      { value: title, weight: 8 },
      { value: keywords, weight: 6 },
      { value: description, weight: 3 },
      { value: type, weight: 1 }
    ];
    const fullText = fields.map((field) => field.value).join(' ');

    if (query.length >= 3 && fullText.includes(query)) {
      return 20 + (title.includes(query) ? 12 : 0);
    }

    let score = 0;
    let matched = 0;
    for (const word of queryTokens) {
      let best = 0;
      for (const field of fields) {
        if (field.value.split(' ').some((part) => part === word)) {
          best = Math.max(best, field.weight);
        } else if (field.value.split(' ').some((part) => part.startsWith(word))) {
          best = Math.max(best, field.weight - 1);
        }
      }
      if (best > 0) {
        matched += 1;
        score += best;
      }
    }
    return matched === queryTokens.length ? score + 2 : 0;
  };

  const render = (catalog, rawQuery) => {
    const query = normalize(rawQuery);
    const queryTokens = tokens(rawQuery);
    results.replaceChildren();

    if (queryTokens.length === 0) {
      status.textContent = 'Escribe un tema o describe brevemente lo que te ocurre para buscar en los contenidos y recursos disponibles.';
      if (suggestions) suggestions.hidden = false;
      return;
    }

    if (suggestions) suggestions.hidden = true;
    if (query.length < 2) {
      status.textContent = 'Escribe un tema o describe brevemente lo que te ocurre para iniciar la búsqueda.';
      return;
    }

    const ranked = catalog
      .filter((item) => item && typeof item.url === 'string' && item.url.startsWith('/') && !item.url.startsWith('//'))
      .map((item) => ({ item, score: rankItem(item, query, queryTokens) }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title, 'es'));

    if (ranked.length === 0) {
      status.textContent = `No hemos encontrado resultados para «${rawQuery.trim()}». Prueba con otra palabra o explora las áreas de aprendizaje.`;
      return;
    }

    status.textContent = `${ranked.length} ${ranked.length === 1 ? 'resultado encontrado' : 'resultados encontrados'} para «${rawQuery.trim()}».`;
    const fragment = document.createDocumentFragment();
    ranked.forEach(({ item }) => fragment.append(createResult(item)));
    results.append(fragment);
  };

  const syncQuery = (value) => {
    const url = new URL(window.location.href);
    if (value.trim()) url.searchParams.set('q', value.trim());
    else url.searchParams.delete('q');
    window.history.replaceState({}, '', url);
  };

  fetch('/search-index.json', { credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((catalog) => {
      if (!Array.isArray(catalog)) throw new Error('Índice de búsqueda no válido');
      const initialQuery = new URLSearchParams(window.location.search).get('q') || '';
      input.value = initialQuery;
      render(catalog, initialQuery);

      form.addEventListener('submit', (event) => {
        event.preventDefault();
        const query = input.value.trim();
        syncQuery(query);
        render(catalog, query);
      });

      input.addEventListener('input', () => {
        const query = input.value.trim();
        syncQuery(query);
        render(catalog, query);
      });
    })
    .catch(() => {
      status.textContent = 'No se ha podido cargar el índice de búsqueda. Puedes explorar todas las áreas de aprendizaje y los recursos desde los enlaces de esta página.';
    });
})();
