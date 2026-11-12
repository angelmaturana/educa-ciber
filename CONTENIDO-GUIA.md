# CONTENIDO-GUIA.md · EDUCA CIBER

Guía rápida de referencia para crear contenidos homogéneos. Basada en `PLAN-CONTENIDO-FINAL.md` §2.

---

## 1. Reglas de oro

1. **No inventar hechos.** Cifras, fechas, artículos de ley, teléfonos solo si se verifican en fuente oficial (INCIBE, OSI, AEPD, CCN-CERT, Policía, Guardia Civil, ENISA, CISA, NIST…). Ante duda: explicar el principio sin dato concreto.
2. **No copiar literalmente.** Estudiar la fuente y redactar con palabras y ejemplos propios.
3. **Ejemplos siempre ficticios** y marcados: `EJEMPLO FICTICIO`. Nunca marcas reales: "Banco XYZ", "Tienda Ejemplo".
4. **Consejos estables, no de interfaz.** Evitar "botón azul arriba a la derecha". Explicar ruta genérica ("Ajustes → Seguridad") y avisar: los menús cambian.
5. **Teléfonos/organismos de ayuda:** solo si se verifican en web oficial en esa sesión; si no, enlazar a la página oficial sin copiar el número.
6. **Sin instrucciones para atacar.** Nada de "cómo hacer phishing", "cómo craquear contraseña". Explicar reconocimiento y defensa.
7. **Tono:** `tú`, cercano, sin tecnicismos; primer término técnico siempre explicado. Español de España.
8. **Consejos legales/normativos (RGPD, denuncias):** nota obligatoria: "Información general; no sustituye asesoramiento legal."
9. **Sin JS, sin recursos externos, sin dependencias.** Solo clases CSS existentes. No tocar `legible/` ni `tests/`. No Git salvo petición.

---

## 2. Anatomía de una lección (copiar de `phishing/index.html`)

**Ruta:** `src/pages/aprende/<hub>/<slug>/index.html`  
(Excepción heredada: fraudes en `aprende/fraudes/<slug>/`; no cambiar URL de phishing)

**Front-matter:**
- `title` ≤ 60 car., único, termina en ` | EDUCA CIBER`
- `description` 120-155 car., único
- `updated` fecha de hoy `YYYY-MM-DD`

**JSON-LD `WebPage`** (igual que phishing)

**`<main id="main">` con:**
1. **Hero:** breadcrumbs (`Inicio / Aprende / Área / Lección`), `eyebrow` con el área, `h1`, `lead`, `meta-row` (nivel · duración · público)
2. **`key-takeaway`**: una frase que recordar
3. **Lo esencial** (`h2`, ≈ 5 min): definición en lenguaje llano + `callout callout-blue` con la idea clave
4. **Aprende** (`h2`, ≈ 15 min): explicación con ejemplo cotidiano. Clases según convenga:
   - `signal-grid` (señales)
   - `steps-list` (pasos)
   - `compare-grid` (comparar opciones)
   - `fake-message` (ejemplo ficticio)
   - `flow-steps` (secuencia)
   - `callout-warn` (error frecuente)
5. **Qué hacer si ya ha pasado** (cuando aplique) con enlace al recurso "qué hacer si…"
6. **Ponte a prueba**: 1-2 `quiz-card` con `<details>` (caso práctico + respuesta razonada)
7. **Preguntas frecuentes** (3 preguntas como `h3` + párrafo; sin JSON-LD FAQ salvo coincidencia exacta)
8. **Fuentes y revisión**: párrafo + `source-links` (2-3 enlaces verificados) + `page-note` "Última revisión editorial: DD/MM/AAAA. Revisión técnica y editorial pendiente antes de publicación definitiva."
9. **`aside`**: "En esta página" con anclajes reales (`#id` de los `h2`) + `aside-card` con 2-3 enlaces relacionados

**Tamaño:** 700-900 palabras en `<main>` (mínimo validador: 250). Recursos: 350-600. Píldoras: 300-450.
**Enlaces internos:** mínimo 3 salientes (hub, 1-2 lecciones hermanas, 1 recurso/píldora) y ≥ 1 entrante (lo da el hub).
**Encabezados:** un solo `h1`; no saltar niveles (h2 → h3).

---

## 3. Checklist mecánico al cerrar CADA lección

- [ ] Añadir objeto a `src/static/search-index.json` (`title`, `url`, `description`, `type`, `keywords`; incluir términos técnicos **y** coloquiales: "me han hackeado", "mensaje raro"…). Solo palabras clave que la página realmente explique.
- [ ] En el hub del área: convertir el tema de `<span>…Contenido en preparación` en enlace `<a href="…">Título <span>Leer contenido →</span></a>` (patrón phishing) y actualizar su `updated`.
- [ ] Enlazar la lección desde al menos una lección hermana ya existente (evita huérfanas).
- [ ] `updated` con la fecha de hoy.

---

## 4. Regla de indexación de los hubs

Cada hub tiene `robots: noindex, follow`. Se **elimina esa línea** (y se reescribe el hub con ≥ 250 palabras: introducción, "ruta recomendada" en orden, para quién es, enlaces a recursos) **cuando el área tiene ≥ 3 lecciones publicadas**. Las fases lo indican como "Cierre de hub". Temas sin lección se quedan como "Próximamente" (sin enlace).

---

## 5. Verificación (al final de cada sesión)

```bash
python3 -B -m unittest discover tests        # esperado: OK
python3 -B legible/build.py --all            # esperado: sin avisos (sin "thin content", sin enlaces rotos)
python3 -B legible/check_site.py --prelaunch # solo en fases de cierre
```

Informar cada comprobación como PASS / FAIL / NOT RUN con la salida real. Si falla un test, comprobar primero si lo causó el cambio; nunca debilitar un test ni una regla del validador.

---

## 6. Hechos sensibles: verificar en fuente oficial ANTES de publicar

| Afirmación | Fuente a consultar | Si no se verifica |
|---|---|---|
| Línea de ayuda 017 de INCIBE (qué atiende, horario, gratuidad) | incibe.es | Enlazar a INCIBE sin copiar el número |
| Canal Prioritario de la AEPD (retirada urgente de contenido sensible) | aepd.es | Enlazar a la AEPD |
| Derechos RGPD (acceso, rectificación, supresión…) y plazos | aepd.es | Nombrar derechos sin plazos |
| Directiva NIS2: obligaciones de la cadena de suministro y aviso temprano en 24 h | Fuentes oficiales UE/CCN/INCIBE | "Las entidades obligadas deben notificar con rapidez"; sin cifra |
| eIDAS 2 y cartera de identidad digital europea (estado actual) | Fuente oficial UE | Omitir o "en desarrollo" |
| SCA / 3D Secure (autenticación reforzada) | Banco de España / norma | Explicar el concepto sin citar norma |
| "No pagar el rescate" (ransomware) | INCIBE / CCN-CERT / Policía | Presentarlo como recomendación general solo si se confirma |
| Bloqueo por IMEI vs borrado remoto; pasos con la operadora | OSI/INCIBE | Explicar la diferencia en general |
| Mecánica del secuestro de WhatsApp (SMS/buzón de voz) y PIN de dos pasos | OSI/INCIBE y ayuda oficial de la app | Describir la defensa (activar verificación en dos pasos) sin detallar menús |
| Edades mínimas legales y consentimiento de menores | AEPD / normativa | No citar edades |
| Textos legales obligatorios de una tienda (aviso legal, identificación, devoluciones) | Fuente oficial consumo | Lista general de "qué debería poder comprobar" |

**Reglas adicionales del Plan Maestro:**
- Sin victimización ni guiones literales en temas de menores; preservar pruebas (no borrar nada).
- Sin marcas, productos ni casos mediáticos con nombre propio como ejemplo de estafa. Plataformas solo en lecciones específicas, sin críticas ni afirmaciones sobre sus políticas.
- Temas ofensivos (OSINT, doxing, clonación de voz) siempre desde la **defensa**: qué se puede hacer con tus datos públicos y cómo reducir exposición, nunca cómo ejecutarlo.

---

## 7. Plantilla canónica (`src/pages/example/index.html`)

Ver archivo `src/pages/example/index.html` — contiene la estructura completa con marcadores `TÍTULO/SLUG/HUB`, todas las clases CSS estándar (`signal-grid`, `steps-list`, `compare-grid`, `fake-message`, `flow-steps`, `quiz-card`, `callout`, `callout-warn`, `key-takeaway`, `source-links`, `page-note`, breadcrumbs, `eyebrow`, `meta-row`, JSON-LD `WebPage`, aside con anclajes reales).

---

## 8. Script `legible/nueva_leccion.py` (modo motor)

**Entrada (JSON por lección):**
```json
{
  "titulo": "...",
  "slug": "...",
  "hub": "...",
  "descripcion": "...",
  "nivel": "básico|intermedio|avanzado",
  "duracion": "5 min · Lo esencial",
  "publico": "todos|familias|empresas|...",
  "idea_clave": "...",
  "esencial": "...",
  "secciones": [
    {"tipo": "signal-grid|steps-list|compare-grid|fake-message|flow-steps|callout-warn", "contenido": "..."}
  ],
  "quiz": [{"pregunta": "...", "respuesta": "..."}],
  "faq": [{"pregunta": "...", "respuesta": "..."}],
  "fuentes": [{"titulo": "...", "url": "..."}],
  "relacionadas": [{"slug": "...", "texto": "..."}]
}
```

**Salida:**
- `index.html` con clases estándar y nota "revisión pendiente"
- Entrada en `src/static/search-index.json`
- Enlace en el hub (de `<span>Contenido en preparación` a `<a>`)
- `updated` de hoy

**Seguridad:** Avisa y no sobrescribe si el slug existe o falta un campo.

**Probarlo:** con una lección real y documentarlo en este archivo.