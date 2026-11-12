# CONTENIDO-GUIA · EDUCA CIBER

Resumen de una página del §2 de `PLAN-CONTENIDO-FINAL.md`. Se consulta al escribir cualquier lección, recurso o píldora.

## 1. Reglas de oro
1. **No inventar hechos.** Ni cifras, ni fechas, ni "estudios", ni multas, ni teléfonos, ni artículos de ley, salvo que se hayan comprobado en fuente oficial esa misma sesión (INCIBE, OSI, AEPD, CCN-CERT, Policía, Guardia Civil, ENISA, CISA, NIST) y se citen. Ante la duda, se explica el principio sin dato.
2. **No copiar literalmente** ninguna fuente: se redacta con palabras y ejemplos propios.
3. **Ejemplos ficticios y marcados** (`EJEMPLO FICTICIO`). Nunca marcas reales en mensajes fraudulentos: "Banco XYZ", "Tienda Ejemplo". Sin casos mediáticos con nombre propio.
4. **Consejos estables**, sin depender de la interfaz: "Ajustes → Seguridad" y aviso de que los menús cambian.
5. **Teléfonos y canales de ayuda** solo si se verifican en la web oficial esa sesión; si no, enlazar sin copiar el número.
6. **Nada que sirva para atacar.** Se explica cómo reconocer y defenderse. Temas ofensivos (OSINT, doxing, clonación de voz) siempre desde la defensa.
7. **Tono:** tú, cercano, español de España; el primer término técnico siempre con su explicación. Sin culpar a la víctima.
8. Consejos legales o normativos (RGPD, derechos, denuncias): nota «Información general; no sustituye asesoramiento legal.» (en el JSON: `"aviso_legal": true`).
9. Sin JavaScript, sin recursos externos, solo clases CSS existentes. No tocar `legible/` ni `tests/` (salvo modo motor autorizado). No ejecutar Git salvo petición.

## 2. Anatomía de una lección
Ruta: `src/pages/aprende/<hub>/<slug>/index.html` (las de fraudes: `aprende/fraudes/<slug>/`). Modelo vivo: `/aprende/fraudes/phishing/`. Plantilla: `src/pages/example/index.html` (`noindex`; los tests exigen que conserve un `.card-grid` con ≥ 3 `.card`, no lo quites).

- **Front-matter:** `title` ≤ 60 car. incluido ` | EDUCA CIBER` (igual que el `name` del JSON-LD), `description` 120-155 car. y única, `updated` de hoy.
- **Orden:** hero (breadcrumbs, `eyebrow`, `h1`, `lead`, `meta-row`) → `key-takeaway` → **Lo esencial** (+ `callout-blue`) → **Aprende** (`signal-grid`, `steps-list`, `compare-grid`, `fake-message`, `flow-steps`, `callout-warn`) → **¿Y si ya ha pasado?** (con enlace al recurso) → **Ponte a prueba** (1-2 `quiz-card`) → **Preguntas frecuentes** (3 × `h3` + párrafo, sin JSON-LD FAQ) → **Fuentes y revisión** (2-3 `source-links` + `page-note` «Revisión técnica y editorial pendiente antes de publicación definitiva») → `aside` («En esta página» con `#id` reales de los `h2` + enlaces relacionados).
- **Tamaño:** lección 700-900 palabras en `<main>` (el validador exige 250); recurso 350-600; píldora 300-450.
- **Enlaces:** ≥ 3 salientes (hub, 1-2 hermanas, 1 recurso o píldora) y ≥ 1 entrante. Un solo `h1`; `h2` → `h3` sin saltos.

## 3. Checklist al cerrar CADA lección
- [ ] Entrada en `src/static/search-index.json` (`title`, `url`, `description`, `type`, `keywords`; términos técnicos **y** cómo lo diría una persona; solo lo que la página explica).
- [ ] En el hub: tema pasa de `<span>…Contenido en preparación` a `<a href="…">Título <span>Leer contenido →</span></a>` y se actualiza su `updated`.
- [ ] Enlazada desde al menos una lección hermana ya existente (evita huérfanas).
- [ ] `updated` con la fecha de hoy.
- [ ] Hub con ≥ 3 lecciones: reescribir (≥ 250 palabras, ruta recomendada en orden) y **quitar** `robots: noindex, follow`.
- [ ] Verificación: `python3 -B -m unittest discover tests` · `python3 -B legible/build.py --all` · (fases de cierre) `python3 -B legible/check_site.py --prelaunch`. Informar PASS / FAIL / NOT RUN con la salida real; nunca debilitar un test ni una regla.

## 4. Hechos sensibles: verificar en fuente oficial ANTES de publicar
Si no se puede consultar, se redacta el principio sin el dato y se anota en `PROGRESO.md` → «Pendientes de verificar».

| Afirmación | Fuente | Si no se verifica |
|---|---|---|
| Línea 017 de INCIBE (qué atiende, horario, gratuidad) | incibe.es | Enlazar sin copiar el número |
| Canal Prioritario de la AEPD | aepd.es | Enlazar a la AEPD |
| Derechos RGPD y plazos | aepd.es | Nombrar derechos sin plazos |
| NIS2: cadena de suministro y aviso temprano en 24 h | UE / CCN / INCIBE | «Notificar con rapidez», sin cifra |
| eIDAS 2 y cartera de identidad digital | Fuente oficial UE | Omitir o «en desarrollo» |
| SCA / 3D Secure | Banco de España / norma | Explicar el concepto sin citar norma |
| «No pagar el rescate» (ransomware) | INCIBE / CCN-CERT / Policía | Solo si se confirma |
| Bloqueo por IMEI vs borrado remoto | OSI / INCIBE | Diferencia en general |
| Secuestro de WhatsApp (SMS/buzón) y PIN | OSI / INCIBE / ayuda oficial | Defensa sin menús |
| Edades mínimas y consentimiento de menores | AEPD / normativa | No citar edades |
| Textos legales obligatorios de una tienda | Fuente oficial de consumo | Lista de «qué debería poder comprobar» |

Menores y temas sensibles: sin victimización, sin guiones literales del agresor, **preservar pruebas (no borrar nada)**, el menor nunca es culpable.

## 5. Crear una lección con el script
`legible/nueva_leccion.py` (solo biblioteca estándar) escribe la lección con las clases estándar, añade la entrada al buscador y convierte el tema del hub en enlace. **Antes de escribir nada** valida todo: si falta un campo, hay un enlace interno roto, el título pasa de 60 caracteres o la carpeta ya existe, avisa y no toca ningún archivo (nunca sobrescribe).

```bash
python3 -B -I legible/nueva_leccion.py --plantilla-json > leccion.json   # JSON de ejemplo con todos los campos
python3 -B -I legible/nueva_leccion.py leccion.json --dry-run             # comprueba y cuenta palabras, sin escribir
python3 -B -I legible/nueva_leccion.py leccion.json                       # crea la lección
```
Opciones: `--fecha AAAA-MM-DD` (por defecto hoy), `--root` (por defecto, la carpeta que contiene `legible/`). El JSON y los archivos de lección pueden vivir fuera de `src/`; no los dejes dentro del sitio.

**Campos obligatorios:** `titulo`, `slug`, `hub` (carpeta del área, p. ej. `fraudes-y-enganos`, `contrasenas-y-cuentas`), `descripcion`, `nivel` (`básico` | `intermedio` | `avanzado`), `duracion`, `publico`, `idea_clave`, `esencial`, `secciones[]`, `quiz[]`, `faq[]`, `fuentes[]`, `relacionadas[]` y `keywords[]` (este último no figuraba en el plan, pero el buscador lo necesita).
**Opcionales:** `titulo_pagina` (título largo de `<title>` y buscador), `titulo_destacado` (final del `h1` en azul), `titulo_breadcrumb`, `lead`, `tema_hub` (texto exacto del tema pendiente en el hub), `nota_fuentes`, `aviso_legal`, `si_ya_ha_pasado` (sección extra con `titulo` y `bloques`).

- `esencial`: lista de párrafos, o `{"parrafos": [...], "callout": {"titulo", "texto"}}`.
- `secciones[]`: `{"titulo", "tiempo"?, "id"?, "bloques": [...]}`. Un bloque es un texto (párrafo) o `{"tipo": …}` con: `parrafo`, `lista`, `senales`, `pasos`, `comparar` (2-3 elementos), `mensaje` (ficticio), `flujo`, `aviso` (`callout-warn`), `idea` (`callout-blue`), `boton`, `subtitulo`.
- En cualquier texto: `**negrita**` y `[texto](/ruta/)` (los enlaces internos se comprueban; los externos deben ser `https://`). Todo lo demás se escapa.
- `quiz[]`: `{"caso", "pregunta", "respuesta", "explicacion"}` · `faq[]`: `{"pregunta", "respuesta"}` · `fuentes[]`: `{"texto", "url"}` · `relacionadas[]`: `{"texto", "url"}` (internas).

Avisos (no bloquean): descripción fuera de 120-155, ≠ 3 preguntas, fuentes o relacionadas fuera de 2-3, palabras fuera de 700-900, tema no encontrado en el hub (en ese caso lo añade al final de la lista).
**No lo hace el script:** enlazar la lección desde una hermana, quitar `noindex` del hub ni verificar hechos. Eso sigue en la checklist del §3.
