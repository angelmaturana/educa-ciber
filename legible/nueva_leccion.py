#!/usr/bin/env python3
"""nueva_leccion: crea una lección de EDUCA CIBER a partir de un JSON.

Solo biblioteca estándar. Ejecutar siempre así, desde la raíz del proyecto:

    python3 -B -I legible/nueva_leccion.py leccion.json            # crea la lección
    python3 -B -I legible/nueva_leccion.py leccion.json --dry-run  # solo comprueba y cuenta palabras
    python3 -B -I legible/nueva_leccion.py --plantilla-json        # imprime un JSON de ejemplo

Qué hace (y solo eso):
  1. escribe src/pages/aprende/<área>/<slug>/index.html con las clases estándar;
  2. añade la entrada a src/static/search-index.json;
  3. en el hub del área, convierte el tema "Contenido en preparación" en enlace y actualiza su `updated`.

Qué NO hace: no toca legible/build.py, check_site.py ni tests/, no sobrescribe nada (si la carpeta de la
lección existe, avisa y para) y no escribe nada si falta un campo o hay un enlace roto. Todo se valida
antes de escribir el primer archivo. No inventa contenido: lo que escribas en el JSON es lo que se publica.
Los hechos (cifras, teléfonos, leyes) los tiene que haber verificado quien escribe el JSON; ver CONTENIDO-GUIA.md.
"""
import argparse
import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

SUFFIX = ' | EDUCA CIBER'
TITLE_MAX, TITLE_MIN = 60, 20          # mismos límites que el validador
DESC_MIN, DESC_MAX = 70, 160           # límites duros del validador
DESC_GOOD = (120, 155)                 # recomendado por la guía
WORDS_GOOD = (700, 900)                # recomendado por la guía (el validador exige >= 250)
LEVELS = ('básico', 'intermedio', 'avanzado')
FRAUD_HUB = 'fraudes-y-enganos'        # excepción heredada: sus lecciones viven en aprende/fraudes/<slug>/
FRAUD_DIR = 'fraudes'
PENDING = 'Contenido en preparación'
RESERVED_IDS = ('main', 'esencial', 'ponte-a-prueba', 'faq', 'fuentes')

REQUIRED = ('titulo', 'slug', 'hub', 'descripcion', 'nivel', 'duracion', 'publico', 'idea_clave',
            'esencial', 'secciones', 'quiz', 'faq', 'fuentes', 'relacionadas', 'keywords')
OPTIONAL = ('titulo_pagina', 'titulo_destacado', 'titulo_breadcrumb', 'lead', 'tema_hub',
            'nota_fuentes', 'aviso_legal', 'si_ya_ha_pasado')

SAMPLE = {
    'titulo': 'Título de la lección',
    'titulo_pagina': 'Título de página opcional (máx. 46)',
    'titulo_destacado': 'final del h1 en azul.',
    'titulo_breadcrumb': 'Título corto',
    'tema_hub': 'Tema del hub',
    'slug': 'slug-de-la-leccion',
    'hub': 'fraudes-y-enganos',
    'descripcion': 'Entre 120 y 155 caracteres, única en todo el sitio, que resuma lo que aprenderá la persona en la lección.',
    'lead': 'Una o dos frases bajo el título.',
    'nivel': 'básico',
    'duracion': '20 min',
    'publico': 'Para todos',
    'idea_clave': 'Una sola frase que merezca recordarse.',
    'esencial': {
        'parrafos': ['Definición en lenguaje llano con un **término técnico** explicado.'],
        'callout': {'titulo': 'La idea clave', 'texto': 'La idea que sostiene la lección.'},
    },
    'secciones': [
        {'titulo': 'Aprende a comprobar', 'tiempo': '15 MIN', 'bloques': [
            'Un párrafo es una cadena de texto. Admite **negrita** y [enlaces](/aprende/fraudes/phishing/).',
            {'tipo': 'senales', 'items': [{'titulo': 'Señal', 'texto': 'Qué observar.'}]},
            {'tipo': 'pasos', 'items': [{'titulo': 'Paso uno.', 'texto': 'Detalle breve.'}]},
            {'tipo': 'comparar', 'items': [{'titulo': 'Opción A', 'texto': 'Ventajas y límites.'},
                                          {'titulo': 'Opción B', 'texto': 'Ventajas y límites.'}]},
            {'tipo': 'mensaje', 'remitente': 'Banco XYZ', 'contexto': 'Notificación', 'texto': 'Texto ficticio.',
             'boton': 'BOTÓN', 'pie': 'Qué debe notar quien lo lee.'},
            {'tipo': 'flujo', 'pasos': ['Uno', 'Dos', 'Tres']},
            {'tipo': 'aviso', 'titulo': 'Error frecuente', 'texto': 'Qué se hace mal.'},
            {'tipo': 'idea', 'titulo': 'Idea', 'texto': 'Texto.'},
            {'tipo': 'lista', 'items': ['Elemento uno', 'Elemento dos']},
            {'tipo': 'subtitulo', 'texto': 'Un h3'},
            {'tipo': 'boton', 'texto': 'Recurso relacionado →', 'url': '/recursos/he-pulsado-un-enlace-sospechoso/'},
        ]},
    ],
    'si_ya_ha_pasado': {'titulo': '¿Y si ya ha pasado?', 'bloques': ['Qué hacer, en orden.']},
    'quiz': [{'caso': 'Situación realista.', 'pregunta': '¿Qué opción es la más prudente?',
              'respuesta': 'La respuesta, en una frase.', 'explicacion': 'Por qué.'}],
    'faq': [{'pregunta': 'Pregunta como la haría una persona.', 'respuesta': 'Respuesta breve.'}],
    'fuentes': [{'texto': 'INCIBE · Título de la página consultada', 'url': 'https://www.incibe.es/'}],
    'nota_fuentes': 'Párrafo de fuentes (sustituye al estándar).',
    'aviso_legal': False,
    'relacionadas': [{'texto': 'Lección hermana', 'url': '/aprende/fraudes/phishing/'}],
    'keywords': ['término técnico', 'cómo lo diría una persona'],
}


class Problem(Exception):
    """Una condición que impide escribir nada (campo que falta, carpeta existente...)."""


class Ctx:
    """Contexto de una ejecución: raíz del proyecto, fecha y lo que se va encontrando."""

    def __init__(self, root, today):
        self.root = Path(root)
        self.today = today
        self.errors = []
        self.warnings = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    @property
    def pages(self):
        return self.root / 'src' / 'pages'


# ---------------------------------------------------------------- utilidades de texto

def norm(text):
    text = unicodedata.normalize('NFD', str(text))
    return ''.join(c for c in text if not unicodedata.combining(c)).lower().strip()


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', norm(text)).strip('-')


def esc(text):
    return html.escape(str(text), quote=False)


def esc_attr(text):
    return html.escape(str(text), quote=True)


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def url_exists(ctx, url):
    """True si una URL interna ("/a/b/" o "/a/b/#ancla") corresponde a una página de src/pages."""
    path = url.split('#', 1)[0].split('?', 1)[0]
    if path == '/':
        return (ctx.pages / 'index.html').exists()
    rel = path.strip('/')
    return ((ctx.pages / rel / 'index.html').exists() or (ctx.pages / (rel + '.html')).exists()
            or (ctx.root / 'src' / 'static' / rel).is_file())


def check_url(ctx, url, where):
    """Valida un enlace: interno que existe, ancla local o https externo."""
    if not is_text(url):
        ctx.err(f'{where}: enlace vacío')
        return False
    if url.startswith('#'):
        return True
    if url.startswith('/'):
        if not url_exists(ctx, url):
            ctx.err(f'{where}: el enlace interno {url} no existe en src/pages')
            return False
        return True
    if url.startswith('https://'):
        return True
    ctx.err(f'{where}: el enlace {url} debe empezar por "/" (interno) o "https://" (externo)')
    return False


def is_external(url):
    return url.startswith('https://')


_INLINE = re.compile(r'\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)')


def inline(ctx, text, where):
    """Texto con **negrita** y [texto](url) -> HTML escapado. Todo lo demás se escapa tal cual."""
    if not is_text(text):
        ctx.err(f'{where}: texto vacío o que no es texto')
        return ''
    out, pos = [], 0
    for m in _INLINE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(f'<strong>{esc(m.group(1))}</strong>')
        else:
            label, url = m.group(2), m.group(3)
            check_url(ctx, url, where)
            extra = ' target="_blank" rel="noopener"' if is_external(url) else ''
            out.append(f'<a href="{esc_attr(url)}"{extra}>{esc(label)}</a>')
        pos = m.end()
    out.append(esc(text[pos:]))
    return ''.join(out)


# ---------------------------------------------------------------- bloques

def _items(ctx, block, where, fields):
    items = block.get('items')
    if not isinstance(items, list) or not items:
        ctx.err(f'{where}: "items" debe ser una lista con elementos')
        return []
    good = []
    for i, it in enumerate(items, 1):
        if not isinstance(it, dict) or not all(is_text(it.get(f)) for f in fields):
            ctx.err(f'{where}: el elemento {i} necesita {", ".join(fields)}')
        else:
            good.append(it)
    return good


def b_parrafo(ctx, b, where):
    return f'<p>{inline(ctx, b.get("texto"), where)}</p>'


def b_lista(ctx, b, where):
    items = b.get('items')
    if not isinstance(items, list) or not items:
        ctx.err(f'{where}: "items" debe ser una lista con elementos')
        return ''
    lis = ''.join(f'<li>{inline(ctx, t, where)}</li>' for t in items)
    return f'<ul>{lis}</ul>'


def b_senales(ctx, b, where):
    cells = ''.join(
        f'<div><b>{n:02d}</b><strong>{inline(ctx, it["titulo"], where)}</strong><p>{inline(ctx, it["texto"], where)}</p></div>'
        for n, it in enumerate(_items(ctx, b, where, ('titulo', 'texto')), 1))
    return f'<div class="signal-grid">{cells}</div>'


def b_pasos(ctx, b, where):
    lis = ''.join(
        f'<li><strong>{inline(ctx, it["titulo"], where)}</strong><p>{inline(ctx, it["texto"], where)}</p></li>'
        for it in _items(ctx, b, where, ('titulo', 'texto')))
    return f'<ol class="steps-list">{lis}</ol>'


def b_comparar(ctx, b, where):
    items = _items(ctx, b, where, ('titulo', 'texto'))
    if len(items) not in (2, 3):
        ctx.err(f'{where}: "comparar" admite 2 o 3 elementos')
    cells = ''.join(
        f'<article><span>{n:02d}</span><h3>{inline(ctx, it["titulo"], where)}</h3><p>{inline(ctx, it["texto"], where)}</p></article>'
        for n, it in enumerate(items, 1))
    return f'<div class="compare-grid">{cells}</div>'


def b_mensaje(ctx, b, where):
    for f in ('remitente', 'contexto', 'texto', 'pie'):
        if not is_text(b.get(f)):
            ctx.err(f'{where}: "mensaje" necesita {f}')
    sender = str(b.get('remitente') or '?')
    button = f'<div class="fake-button">{esc(b["boton"])}</div>' if is_text(b.get('boton')) else ''
    return (f'<div class="fake-message"><div class="fake-top"><span class="fake-avatar">{esc(sender[:1].upper())}</span>'
            f'<div><strong>{esc(sender)}</strong><small>{esc(b.get("contexto", ""))}</small></div>'
            f'<span class="fake-label">EJEMPLO FICTICIO</span></div><p>“{esc(b.get("texto", ""))}”</p>{button}'
            f'<small class="fake-foot">{esc(b.get("pie", ""))}</small></div>')


def b_flujo(ctx, b, where):
    steps = b.get('pasos')
    if not isinstance(steps, list) or len(steps) < 2 or not all(is_text(s) for s in steps):
        ctx.err(f'{where}: "flujo" necesita "pasos" con al menos 2 textos')
        return ''
    return '<div class="flow-steps">' + '<b>→</b>'.join(f'<span>{esc(s.upper())}</span>' for s in steps) + '</div>'


def _callout(kind):
    def render(ctx, b, where):
        for f in ('titulo', 'texto'):
            if not is_text(b.get(f)):
                ctx.err(f'{where}: "{b.get("tipo")}" necesita {f}')
        return (f'<div class="callout callout-{kind}"><strong>{inline(ctx, b.get("titulo"), where)}</strong>'
                f'<p>{inline(ctx, b.get("texto"), where)}</p></div>')
    return render


def b_boton(ctx, b, where):
    check_url(ctx, b.get('url'), where)
    extra = ' target="_blank" rel="noopener"' if is_external(str(b.get('url', ''))) else ''
    return f'<a class="button primary" href="{esc_attr(b.get("url", ""))}"{extra}>{inline(ctx, b.get("texto"), where)}</a>'


def b_subtitulo(ctx, b, where):
    return f'<h3>{inline(ctx, b.get("texto"), where)}</h3>'


BLOCKS = {'parrafo': b_parrafo, 'lista': b_lista, 'senales': b_senales, 'pasos': b_pasos, 'comparar': b_comparar,
          'mensaje': b_mensaje, 'flujo': b_flujo, 'aviso': _callout('warn'), 'idea': _callout('blue'),
          'boton': b_boton, 'subtitulo': b_subtitulo}


def render_blocks(ctx, blocks, where):
    if not isinstance(blocks, list) or not blocks:
        ctx.err(f'{where}: "bloques" debe ser una lista con elementos')
        return []
    out = []
    for i, block in enumerate(blocks, 1):
        here = f'{where}, bloque {i}'
        if isinstance(block, str):
            block = {'tipo': 'parrafo', 'texto': block}
        if not isinstance(block, dict) or block.get('tipo') not in BLOCKS:
            ctx.err(f'{here}: tipo desconocido (válidos: {", ".join(BLOCKS)})')
            continue
        out.append(BLOCKS[block['tipo']](ctx, block, here))
    return out


# ---------------------------------------------------------------- validación del JSON

def validate(ctx, data):
    if not isinstance(data, dict):
        raise Problem('el JSON debe ser un objeto con los campos de la lección')
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise Problem('faltan campos obligatorios: ' + ', '.join(missing))
    unknown = [k for k in data if k not in REQUIRED and k not in OPTIONAL]
    if unknown:
        ctx.err('campos desconocidos (¿errata?): ' + ', '.join(unknown))
    for k in ('titulo', 'slug', 'hub', 'descripcion', 'nivel', 'duracion', 'publico', 'idea_clave'):
        if not is_text(data[k]):
            ctx.err(f'"{k}" debe ser un texto no vacío')
    for k in ('titulo', 'descripcion', 'titulo_pagina', 'titulo_destacado', 'titulo_breadcrumb', 'lead'):
        if k in data and isinstance(data[k], str) and ('\n' in data[k] or '\r' in data[k]):
            ctx.err(f'"{k}" no puede tener saltos de línea')
    for k in ('secciones', 'quiz', 'faq', 'fuentes', 'relacionadas', 'keywords'):
        if not isinstance(data[k], list) or not data[k]:
            ctx.err(f'"{k}" debe ser una lista con al menos un elemento')
    if is_text(data['slug']) and not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', data['slug']):
        ctx.err('"slug": solo minúsculas sin tildes, números y guiones (por ejemplo "buenas-contrasenas")')
    if is_text(data['nivel']) and data['nivel'] not in LEVELS:
        ctx.err('"nivel" debe ser uno de: ' + ', '.join(LEVELS))
    if ctx.errors:
        raise Problem('hay errores en el JSON')


def title_checks(ctx, data):
    title = f'{data.get("titulo_pagina") or data["titulo"]}{SUFFIX}'
    if len(title) > TITLE_MAX:
        ctx.err(f'el título de página mide {len(title)} caracteres (máximo {TITLE_MAX}, incluido "{SUFFIX}"): usa "titulo_pagina" más corto')
    if len(title) < TITLE_MIN:
        ctx.err(f'el título de página es demasiado corto ({len(title)} caracteres, mínimo {TITLE_MIN})')
    n = len(data['descripcion'])
    if n > DESC_MAX or n < DESC_MIN:
        ctx.err(f'la descripción mide {n} caracteres (el validador exige {DESC_MIN}-{DESC_MAX})')
    elif not DESC_GOOD[0] <= n <= DESC_GOOD[1]:
        ctx.warn(f'la descripción mide {n} caracteres (lo recomendado es {DESC_GOOD[0]}-{DESC_GOOD[1]})')
    return title


# ---------------------------------------------------------------- piezas de la página

def read_hub(ctx, hub):
    path = ctx.pages / 'aprende' / hub / 'index.html'
    if not path.is_file():
        raise Problem(f'el área "{hub}" no existe: no hay {path.relative_to(ctx.root)}')
    text = path.read_text(encoding='utf-8')
    m = re.search(r'<h1>(.*?)</h1>', text, re.S)
    name = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else hub
    return path, text, html.unescape(name)


def render_esencial(ctx, data):
    ess = data['esencial']
    if isinstance(ess, list):
        ess = {'parrafos': ess}
    if not isinstance(ess, dict) or not isinstance(ess.get('parrafos'), list) or not ess['parrafos']:
        ctx.err('"esencial" debe ser una lista de párrafos o un objeto con "parrafos" (y opcional "callout")')
        return ''
    parts = ['<h2 id="esencial">5 MIN · Lo esencial</h2>']
    parts += [f'<p>{inline(ctx, p, "esencial")}</p>' for p in ess['parrafos']]
    call = ess.get('callout')
    if call is not None:
        parts.append(_callout('blue')(ctx, dict(call, tipo='idea') if isinstance(call, dict) else {}, 'esencial.callout'))
    else:
        ctx.warn('"esencial" no tiene "callout": la guía pide un callout-blue con la idea clave')
    return '\n  '.join(parts)


def render_sections(ctx, data):
    sections = list(data['secciones'])
    extra = data.get('si_ya_ha_pasado')
    if extra is not None:
        if not isinstance(extra, dict):
            ctx.err('"si_ya_ha_pasado" debe ser un objeto con "titulo" y "bloques"')
        else:
            sections.append(dict(extra, id=extra.get('id', 'ya-ha-pasado')))
    html_parts, anchors, seen = [], [], set(RESERVED_IDS)
    for n, sec in enumerate(sections, 1):
        where = f'sección {n}'
        if not isinstance(sec, dict) or not is_text(sec.get('titulo')):
            ctx.err(f'{where}: necesita "titulo"')
            continue
        sid = sec.get('id') or slugify(sec['titulo'])
        if not sid or sid in seen:
            ctx.err(f'{where}: el id "{sid}" está repetido o es reservado ({", ".join(RESERVED_IDS)}); añade "id"')
            continue
        seen.add(sid)
        label = f'{sec["tiempo"]} · {sec["titulo"]}' if is_text(sec.get('tiempo')) else sec['titulo']
        body = render_blocks(ctx, sec.get('bloques'), f'{where} ({sec["titulo"]})')
        html_parts.append(f'<h2 id="{esc_attr(sid)}">{esc(label)}</h2>\n  ' + '\n  '.join(body))
        anchors.append((sid, sec['titulo']))
    return '\n  '.join(html_parts), anchors


def render_quiz(ctx, data):
    parts = ['<h2 id="ponte-a-prueba">Ponte a prueba</h2>']
    for i, q in enumerate(data['quiz'], 1):
        if not isinstance(q, dict) or not all(is_text(q.get(f)) for f in ('caso', 'pregunta', 'respuesta', 'explicacion')):
            ctx.err(f'quiz {i}: necesita caso, pregunta, respuesta y explicacion')
            continue
        parts.append(
            f'<div class="quiz-card"><p class="eyebrow">Caso práctico</p><h3>{inline(ctx, q["caso"], f"quiz {i}")}</h3>'
            f'<details><summary>{inline(ctx, q["pregunta"], f"quiz {i}")}</summary><div class="answer">'
            f'<strong>{inline(ctx, q["respuesta"], f"quiz {i}")}</strong><p>{inline(ctx, q["explicacion"], f"quiz {i}")}</p>'
            f'</div></details></div>')
    if not 1 <= len(data['quiz']) <= 2:
        ctx.warn(f'hay {len(data["quiz"])} quiz-card (la guía pide 1-2)')
    return '\n  '.join(parts)


def render_faq(ctx, data):
    parts = ['<h2 id="faq">Preguntas frecuentes</h2>']
    for i, q in enumerate(data['faq'], 1):
        if not isinstance(q, dict) or not all(is_text(q.get(f)) for f in ('pregunta', 'respuesta')):
            ctx.err(f'faq {i}: necesita pregunta y respuesta')
            continue
        parts.append(f'<h3>{inline(ctx, q["pregunta"], f"faq {i}")}</h3><p>{inline(ctx, q["respuesta"], f"faq {i}")}</p>')
    if len(data['faq']) != 3:
        ctx.warn(f'hay {len(data["faq"])} preguntas frecuentes (la guía pide 3)')
    return '\n  '.join(parts)


def render_sources(ctx, data):
    links = []
    for i, f in enumerate(data['fuentes'], 1):
        if not isinstance(f, dict) or not is_text(f.get('texto')) or not is_text(f.get('url')):
            ctx.err(f'fuente {i}: necesita texto y url')
        elif not f['url'].startswith('https://'):
            ctx.err(f'fuente {i}: la URL debe empezar por https://')
        else:
            links.append(f'<li><a href="{esc_attr(f["url"])}" target="_blank" rel="noopener">{esc(f["texto"])}</a></li>')
    if not 2 <= len(data['fuentes']) <= 3:
        ctx.warn(f'hay {len(data["fuentes"])} fuentes (la guía pide 2-3 enlaces verificados)')
    note = data.get('nota_fuentes') or ('Contenido elaborado a partir de documentación de referencia de las fuentes citadas, '
                                         'redactado con palabras propias. Las recomendaciones concretas deben revisarse cuando '
                                         'cambien los servicios, las interfaces o las amenazas.')
    legal = ''
    if data.get('aviso_legal'):
        legal = '<p class="page-note">Información general; no sustituye asesoramiento legal.</p>'
    d = ctx.today
    review = (f'<p class="page-note">Última revisión editorial: {d.day:02d}/{d.month:02d}/{d.year}. '
              'Revisión técnica y editorial pendiente antes de publicación definitiva.</p>')
    return (f'<h2 id="fuentes">Fuentes y revisión</h2><p>{inline(ctx, note, "nota_fuentes")}</p>\n  '
            f'<ul class="source-links">{"".join(links)}</ul>\n  {legal}{review}')


def render_aside(ctx, data, anchors):
    index = [('esencial', 'Lo esencial')] + anchors + [('ponte-a-prueba', 'Ponte a prueba'),
                                                     ('faq', 'Preguntas frecuentes'), ('fuentes', 'Fuentes')]
    toc = ''.join(f'<a href="#{esc_attr(i)}">{esc(t)}</a>' for i, t in index)
    rel = []
    for i, r in enumerate(data['relacionadas'], 1):
        if not isinstance(r, dict) or not is_text(r.get('texto')) or not check_url(ctx, r.get('url'), f'relacionada {i}'):
            ctx.err(f'relacionada {i}: necesita texto y url interna válida')
        else:
            rel.append(f'<a href="{esc_attr(r["url"])}">{esc(r["texto"])}</a>')
    if not 2 <= len(data['relacionadas']) <= 3:
        ctx.warn(f'hay {len(data["relacionadas"])} enlaces relacionados (la guía pide 2-3: hermanas y un recurso)')
    return (f'<aside class="content-aside"><div class="aside-card"><p class="eyebrow">En esta página</p>{toc}</div>'
            f'<div class="aside-card"><p class="eyebrow">Sigue aprendiendo</p>{"".join(rel)}</div></aside>')


def json_ld(title, desc):
    def q(s):
        return json.dumps(s, ensure_ascii=False).replace('<', '\\u003c')
    return ('<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "WebPage",\n'
            '  "@id": "{{page_url}}#webpage",\n  "url": "{{page_url}}",\n'
            f'  "name": {q(title)},\n  "description": {q(desc)},\n  "inLanguage": "{{{{in_language}}}}",\n'
            '  "isPartOf": {"@id": "{{site_url}}/#website"},\n  "about": {"@id": "{{site_url}}/#business"},\n'
            '  "dateModified": "{{page_updated}}"\n}\n</script>')


def build_lesson(ctx, data, hub_name, lesson_url):
    title = title_checks(ctx, data)
    short = data.get('titulo_breadcrumb') or data['titulo']
    hub_url = f'/aprende/{data["hub"]}/'
    h1 = esc(data['titulo']) + (f' <span class="text-blue">{esc(data["titulo_destacado"])}</span>'
                                if is_text(data.get('titulo_destacado')) else '')
    lead = data.get('lead') or data['descripcion']
    esencial = render_esencial(ctx, data)
    sections, anchors = render_sections(ctx, data)
    quiz, faq, sources = render_quiz(ctx, data), render_faq(ctx, data), render_sources(ctx, data)
    aside = render_aside(ctx, data, anchors)
    main_html = f'''<main id="main">
<section class="inner-hero page-width">
 <nav class="breadcrumbs breadcrumb" aria-label="Ruta de navegación"><a href="/">Inicio</a><span>/</span><a href="/aprende/">Aprende</a><span>/</span><a href="{hub_url}">{esc(hub_name)}</a><span>/</span><span>{esc(short)}</span></nav>
 <p class="eyebrow">{esc(hub_name)}</p><h1>{h1}</h1>
 <p class="lead">{esc(lead)}</p>
 <div class="meta-row"><span class="meta-pill">Nivel {esc(data['nivel'])}</span><span class="meta-pill">{esc(data['publico'])}</span><span class="meta-pill">{esc(data['duracion'])}</span></div>
</section>
<section class="section page-width content-layout">
 <article class="content-main">
  <div class="key-takeaway"><span class="eyebrow">Qué debes recordar</span><strong>{inline(ctx, data['idea_clave'], 'idea_clave')}</strong></div>
  {esencial}
  {sections}
  {quiz}
  {faq}
  {sources}
 </article>
 {aside}
</section></main>
'''
    front = f'---\ntitle: {title}\ndescription: {data["descripcion"]}\nupdated: {ctx.today.isoformat()}\n---\n\n'
    words = len(re.sub(r'<[^>]+>', ' ', main_html).split())
    if not WORDS_GOOD[0] <= words <= WORDS_GOOD[1]:
        ctx.warn(f'la página tiene unas {words} palabras en <main> (lo recomendado es {WORDS_GOOD[0]}-{WORDS_GOOD[1]}; el validador exige 250)')
    return front + json_ld(title, data['descripcion']) + '\n' + main_html, words


# ---------------------------------------------------------------- buscador y hub

def update_search(ctx, data, lesson_url):
    path = ctx.root / 'src' / 'static' / 'search-index.json'
    try:
        entries = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise Problem(f'no se pudo leer src/static/search-index.json: {exc}')
    if any(e.get('url') == lesson_url for e in entries):
        ctx.warn(f'{lesson_url} ya estaba en search-index.json: no se añade otra entrada')
        return None
    seen, keywords = set(), []
    for k in data['keywords']:
        if not is_text(k):
            ctx.err('"keywords" solo admite textos no vacíos')
        elif norm(k) not in seen:
            seen.add(norm(k))
            keywords.append(k.strip())
    entries.append({'title': data.get('titulo_pagina') or data['titulo'], 'url': lesson_url,
                    'description': data['descripcion'], 'type': f'Aprende · {data["duracion"]}', 'keywords': keywords})
    return json.dumps(entries, indent=2, ensure_ascii=False) + '\n'


def update_hub(ctx, data, hub_text, lesson_url):
    topic = data.get('tema_hub') or data.get('titulo_breadcrumb') or data['titulo']
    if f'href="{lesson_url}"' in hub_text:
        ctx.warn(f'el hub ya enlaza a {lesson_url}: no se modifica el tema')
        return hub_text
    pattern = re.compile(r'<li><span>([^<]*)</span><small>[^<]*</small></li>')
    for m in pattern.finditer(hub_text):
        if norm(html.unescape(m.group(1))) == norm(topic):
            link = f'<li><a href="{lesson_url}">{m.group(1)} <span>Leer contenido →</span></a></li>'
            new = hub_text[:m.start()] + link + hub_text[m.end():]
            return re.sub(r'(?m)^updated: .*$', f'updated: {ctx.today.isoformat()}', new, count=1)
    end = hub_text.find('</ul>', hub_text.find('class="topic-list"')) if 'class="topic-list"' in hub_text else -1
    if end < 0:
        ctx.warn('el hub no tiene lista de temas (topic-list): enlaza la lección a mano')
        return hub_text
    ctx.warn(f'no encontré el tema "{topic}" pendiente en el hub: he añadido el enlace al final de la lista '
             '(usa "tema_hub" si el tema ya existía con otro nombre)')
    link = f'<li><a href="{lesson_url}">{esc(topic)} <span>Leer contenido →</span></a></li>'
    new = hub_text[:end] + link + hub_text[end:]
    return re.sub(r'(?m)^updated: .*$', f'updated: {ctx.today.isoformat()}', new, count=1)


# ---------------------------------------------------------------- programa

def plan(ctx, data):
    """Valida todo y devuelve lo que habría que escribir: [(ruta, texto)], palabras. No escribe nada."""
    validate(ctx, data)
    hub_path, hub_text, hub_name = read_hub(ctx, data['hub'])
    folder = FRAUD_DIR if data['hub'] == FRAUD_HUB else data['hub']
    rel = f'aprende/{folder}/{data["slug"]}'
    target = ctx.pages / rel / 'index.html'
    lesson_url = f'/{rel}/'
    if target.exists() or target.parent.exists():
        raise Problem(f'{lesson_url} ya existe ({target.relative_to(ctx.root)}): no se sobrescribe. Elige otro slug o bórrala a mano.')
    page, words = build_lesson(ctx, data, hub_name, lesson_url)
    search = update_search(ctx, data, lesson_url)
    hub_new = update_hub(ctx, data, hub_text, lesson_url)
    if ctx.errors:
        raise Problem('hay errores en el contenido')
    writes = [(target, page)]
    if search is not None:
        writes.append((ctx.root / 'src' / 'static' / 'search-index.json', search))
    if hub_new != hub_text:
        writes.append((hub_path, hub_new))
    return writes, words, lesson_url


def parse_args(argv):
    p = argparse.ArgumentParser(prog='nueva_leccion.py', description='Crea una lección de EDUCA CIBER desde un JSON.')
    p.add_argument('json', nargs='?', help='ruta del JSON de la lección')
    p.add_argument('--dry-run', action='store_true', help='comprueba y cuenta palabras sin escribir nada')
    p.add_argument('--plantilla-json', action='store_true', help='imprime un JSON de ejemplo con todos los campos')
    p.add_argument('--fecha', help='fecha YYYY-MM-DD (por defecto, hoy)')
    p.add_argument('--root', help='raíz del proyecto (por defecto, la carpeta que contiene legible/)')
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.plantilla_json:
        print(json.dumps(SAMPLE, indent=2, ensure_ascii=False))
        return 0
    if not args.json:
        print('Falta el JSON de la lección. Uso: python3 -B -I legible/nueva_leccion.py leccion.json', file=sys.stderr)
        return 2
    try:
        today = date.fromisoformat(args.fecha) if args.fecha else date.today()
    except ValueError:
        print('--fecha debe tener el formato YYYY-MM-DD', file=sys.stderr)
        return 2
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    ctx = Ctx(root, today)
    try:
        data = json.loads(Path(args.json).read_text(encoding='utf-8'))
        writes, words, url = plan(ctx, data)
    except (OSError, ValueError) as exc:
        print(f'✗ No se pudo leer el JSON: {exc}', file=sys.stderr)
        return 1
    except Problem as exc:
        print(f'✗ {str(exc).rstrip(".")}. No se ha escrito nada.', file=sys.stderr)
        for e in ctx.errors:
            print(f'  - {e}', file=sys.stderr)
        return 1
    for w in ctx.warnings:
        print(f'⚠ {w}')
    if args.dry_run:
        print(f'✓ Comprobación correcta de {url} (~{words} palabras). No se ha escrito nada (--dry-run).')
        return 0
    for path, text in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
        print(f'  escrito {path.relative_to(ctx.root)}')
    print(f'✓ Lección creada: {url} (~{words} palabras).')
    print('Falta a mano: enlazarla desde al menos una lección hermana ya existente, y ejecutar')
    print('  python3 -B -m unittest discover tests  y  python3 -B legible/build.py --all')
    return 0


if __name__ == '__main__':
    sys.exit(main())
