#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar una nueva lección a partir de un JSON.
Uso: python3 -B -I legible/nueva_leccion.py <archivo_json>
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

REQUIRED_FIELDS = [
    "titulo", "slug", "hub", "descripcion", "nivel", "duracion", "publico",
    "idea_clave", "esencial", "secciones", "quiz", "faq", "fuentes", "relacionadas"
]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_data(data):
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(missing)}")
    if not data["slug"] or not data["hub"]:
        raise ValueError("slug y hub no pueden estar vacíos")

def slugify(text):
    return text.lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

def build_lesson_html(data, today):
    hub_slug = data["hub"].lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    lesson_slug = data["slug"]
    
    # Build sections HTML
    sections_html = ""
    for sec in data["secciones"]:
        if sec["tipo"] == "signal-grid":
            items = ""
            for i, item in enumerate(sec["contenido"], 1):
                items += f'   <div><b>{i:02d}</b><strong>{item["titulo"]}</strong><p>{item["descripcion"]}</p></div>\n'
            sections_html += f'  <h2 id="{sec.get("id", "senales")}">{sec.get("titulo", "¿Qué señales deberían hacerte parar?")}</h2>\n  <div class="signal-grid">\n{items}  </div>\n'
        elif sec["tipo"] == "steps-list":
            steps = ""
            for step in sec["contenido"]:
                steps += f'<li><strong>{step["titulo"]}</strong><p>{step["descripcion"]}</p></li>\n'
            sections_html += f'  <h2 id="{sec.get("id", "aprende")}">{sec.get("titulo", "15 MIN · Aprende a comprobar")}</h2>\n  <p>{sec.get("intro", "")}</p>\n  <ol class="steps-list">\n{steps}  </ol>\n'
        elif sec["tipo"] == "fake-message":
            sections_html += f'  <h2 id="{sec.get("id", "ejemplo")}">{sec.get("titulo", "Un ejemplo: situación cotidiana")}</h2>\n  <div class="fake-message"><div class="fake-top"><span class="fake-avatar">{sec.get("avatar", "E")}</span><div><strong>{sec.get("entidad", "Entidad Ejemplo")}</strong><small>{sec.get("asunto", "Asunto")}</small></div><span class="fake-label">EJEMPLO FICTICIO</span></div><p>{sec.get("texto", "")}</p><div class="fake-button">{sec.get("boton", "BOTÓN")}</div><small class="fake-foot">{sec.get("nota", "")}</small></div>\n  <p>{sec.get("preguntas", "")}</p>\n'
        elif sec["tipo"] == "flow-steps":
            steps = "".join([f'<span>{s}</span><b>→</b>' for s in sec["contenido"][:-1]]) + f'<span>{sec["contenido"][-1]}</span>'
            sections_html += f'  <div class="flow-steps">{steps}</div>\n'
        elif sec["tipo"] == "callout-warn":
            sections_html += f'  <div class="callout callout-warn"><strong>{sec.get("titulo", "Error frecuente")}</strong><p>{sec["contenido"]}</p></div>\n'
        elif sec["tipo"] == "compare-grid":
            items = ""
            for item in sec["contenido"]:
                items += f'   <div><strong>{item["titulo"]}</strong><p>{item["descripcion"]}</p></div>\n'
            sections_html += f'  <h2 id="{sec.get("id", "comparar")}">{sec.get("titulo", "Comparar opciones")}</h2>\n  <div class="compare-grid">\n{items}  </div>\n'
        else:
            sections_html += f'  <!-- Sección tipo desconocido: {sec["tipo"]} -->\n'

    # Build quiz HTML
    quiz_html = ""
    for q in data["quiz"]:
        quiz_html += f'  <div class="quiz-card"><p class="eyebrow">Caso práctico</p><h3>{q["pregunta"]}</h3><details><summary>¿Qué opción es la más prudente?</summary><div class="answer"><strong>{q["respuesta"]}</strong></div></details></div>\n'

    # Build FAQ HTML
    faq_html = ""
    for f in data["faq"]:
        faq_html += f'  <h3>{f["pregunta"]}</h3>\n  <p>{f["respuesta"]}</p>\n'

    # Build sources HTML
    sources_html = ""
    for f in data["fuentes"]:
        sources_html += f'  <li><a href="{f["url"]}" target="_blank" rel="noopener">{f["titulo"]}</a></li>\n'

    # Build related lessons HTML
    related_html = ""
    for r in data["relacionadas"]:
        related_hub = r.get("hub", data["hub"])
        related_tipo = r.get("tipo", "")
        if related_tipo == "pildora":
            related_html += f'  <a href="/pildora/{r["slug"]}/">{r["texto"]}</a>\n'
        elif related_hub:
            related_hub_slug = related_hub.lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
            related_html += f'  <a href="/aprende/{related_hub_slug}/{r["slug"]}/">{r["texto"]}</a>\n'
        else:
            related_html += f'  <a href="/{r["slug"]}/">{r["texto"]}</a>\n'

    # Build aside anchors
    aside_anchors = '<a href="#lo-esencial">Lo esencial</a><a href="#senales">Señales de alerta</a><a href="#aprende">Cómo comprobar</a><a href="#ejemplo">Ejemplo</a><a href="#que-hacer">Qué hacer si ya ha pasado</a><a href="#ponte-a-prueba">Ponte a prueba</a><a href="#faq">Preguntas frecuentes</a><a href="/aprende/{}/">Volver al hub</a>'.format(hub_slug)

    html = f'''---
title: {data["titulo"]} | EDUCA CIBER
description: {data["descripcion"]}
updated: {today}
---

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": "{{{{page_url}}}}#webpage",
  "url": "{{{{page_url}}}}",
  "name": "{data["titulo"]} | EDUCA CIBER",
  "description": "{data["descripcion"]}",
  "inLanguage": "{{{{in_language}}}}",
  "isPartOf": {{"@id": "{{{{site_url}}}}/#website"}},
  "about": {{"@id": "{{{{site_url}}}}/#business"}},
  "dateModified": "{{{{page_updated}}}}"
}}
</script>
<main id="main">
<section class="inner-hero page-width">
 <nav class="breadcrumbs breadcrumb" aria-label="Ruta de navegación"><a href="/">Inicio</a><span>/</span><a href="/aprende/">Aprende</a><span>/</span><a href="/aprende/{hub_slug}/">{data["hub"]}</a><span>/</span><span>{data["titulo"]}</span></nav>
 <p class="eyebrow">{data["hub"]} · Contenido piloto</p><h1>{data["titulo"]} <span class="text-blue">{data.get("gancho", "")}</span></h1>
 <p class="lead">{data.get("lead", "")}</p>
 <div class="meta-row"><span class="meta-pill">{data["nivel"]}</span><span class="meta-pill">{data["publico"]}</span><span class="meta-pill">{data["duracion"]}</span></div>
</section>
<section class="section page-width content-layout">
 <article class="content-main">
  <div class="key-takeaway"><span class="eyebrow">Qué debes recordar</span><strong>{data["idea_clave"]}</strong></div>
  <h2 id="lo-esencial">5 MIN · Lo esencial</h2>
  <p>{data["esencial"]}</p>
  <div class="callout callout-blue"><strong>La idea clave</strong><p>{data["idea_clave"]}</p></div>
{sections_html}
  <h2 id="que-hacer">¿Y si ya ha pasado?</h2>
  <p>Qué hacer si el usuario ya ha interactuado con la amenaza. Enlaza al recurso correspondiente.</p>
  <a class="button primary" href="/recursos/he-pulsado-un-enlace-sospechoso/">He pulsado un enlace sospechoso: ¿qué hago? →</a>
  <h2 id="ponte-a-prueba">Ponte a prueba</h2>
{quiz_html}
  <h2 id="faq">Preguntas frecuentes</h2>
{faq_html}
  <h2 id="fuentes">Fuentes y revisión</h2><p>Contenido elaborado a partir de documentación de referencia de INCIBE, OSI u otras fuentes oficiales. Las recomendaciones concretas deben revisarse cuando cambien los servicios, las interfaces o las amenazas.</p>
  <ul class="source-links">
{sources_html}  </ul>
  <p class="page-note">Última revisión editorial: {today[8:10]}/{today[5:7]}/{today[0:4]}. Revisión técnica y editorial pendiente antes de publicación definitiva.</p>
 </article>
 <aside class="content-aside"><div class="aside-card"><p class="eyebrow">En esta página</p>{aside_anchors}</div><div class="aside-card aside-highlight"><strong>¿Tienes un problema ahora?</strong><p>Si necesitas actuar ya, empieza por esta guía práctica.</p><a href="/recursos/he-pulsado-un-enlace-sospechoso/">Ver qué hacer →</a></div><div class="aside-card"><p class="eyebrow">Lecciones relacionadas</p>
{related_html}</div></aside>
</section></main>
'''
    return html

def update_search_index(data, today):
    search_index_path = Path("src/static/search-index.json")
    with open(search_index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    hub_slug = data["hub"].lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    lesson_slug = data["slug"]
    url = f"/aprende/{hub_slug}/{lesson_slug}/"
    
    # Check if already exists
    for entry in index:
        if entry["url"] == url:
            raise ValueError(f"La lección ya existe en search-index.json: {url}")
    
    # Build keywords
    keywords = [
        data["titulo"].lower(),
        data["slug"].replace("-", " "),
        data["hub"].lower(),
        "ciberseguridad",
        "aprender",
        "seguridad digital"
    ]
    # Add technical and colloquial terms
    for sec in data["secciones"]:
        if sec["tipo"] == "signal-grid":
            for item in sec["contenido"]:
                keywords.append(item["titulo"].lower())
    
    new_entry = {
        "title": data["titulo"],
        "url": url,
        "description": data["descripcion"],
        "type": f"Aprende · {data['duracion']}",
        "keywords": list(set(keywords))  # deduplicate
    }
    
    index.append(new_entry)
    
    with open(search_index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def update_hub(data):
    hub_slug = data["hub"].lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    lesson_slug = data["slug"]
    hub_path = Path(f"src/pages/aprende/{hub_slug}/index.html")
    
    if not hub_path.exists():
        raise ValueError(f"Hub no encontrado: {hub_path}")
    
    with open(hub_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update the topic list: replace <span>Lesson Title</span><small>Contenido en preparación</small> with link
    old_pattern = f'<span>{data["titulo"]}</span><small>Contenido en preparación</small>'
    new_pattern = f'<a href="/aprende/{hub_slug}/{lesson_slug}/">{data["titulo"]} <span>Leer contenido →</span></a>'
    
    if old_pattern not in content:
        # Try alternative pattern
        old_pattern2 = f'<span>{data["titulo"]}</span><small>Próximamente</small>'
        if old_pattern2 in content:
            old_pattern = old_pattern2
        else:
            raise ValueError(f"No se encontró el tema en el hub: {data['titulo']}")
    
    content = content.replace(old_pattern, new_pattern)
    
    # Update the updated date
    today = date.today().isoformat()
    import re
    content = re.sub(r'updated: \d{4}-\d{2}-\d{2}', f'updated: {today}', content)
    content = re.sub(r'dateModified": "\{\{page_updated\}\}"', f'dateModified": "{{page_updated}}"', content)  # keep template
    
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 -B -I legible/nueva_leccion.py <archivo_json>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"Error: Archivo no encontrado: {json_path}")
        sys.exit(1)
    
    data = load_json(json_path)
    validate_data(data)
    
    hub_slug = data["hub"].lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    lesson_slug = data["slug"]
    lesson_dir = Path(f"src/pages/aprende/{hub_slug}/{lesson_slug}")
    lesson_file = lesson_dir / "index.html"
    
    if lesson_file.exists():
        print(f"Error: La lección ya existe: {lesson_file}")
        sys.exit(1)
    
    today = date.today().isoformat()
    
    # Generate HTML
    html = build_lesson_html(data, today)
    
    # Create directory and write file
    lesson_dir.mkdir(parents=True, exist_ok=True)
    with open(lesson_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    # Update search index
    update_search_index(data, today)
    
    # Update hub
    update_hub(data)
    
    print(f"✓ Lección creada: {lesson_file}")
    print(f"✓ Entrada añadida a search-index.json")
    print(f"✓ Hub actualizado: /aprende/{hub_slug}/")
    print(f"✓ Fecha updated: {today}")

if __name__ == "__main__":
    main()