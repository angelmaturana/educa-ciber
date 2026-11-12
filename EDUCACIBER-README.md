# EDUCA CIBER · Notas de proyecto

## Contacto

- Contacto general: `hola@educaciber.com` (único canal general).
- Contacto legal y privacidad: `legal@educaciber.com`.
- No hay teléfono ni WhatsApp configurados.

Los correos se mantienen en `src/data/site.json`. Las páginas legales muestran únicamente el correo legal como dato de contacto; esta decisión visual no sustituye la revisión de los datos obligatorios que puedan ser exigibles según la actividad y la normativa aplicable.

## Buscador

El buscador de `/buscar/` funciona íntegramente en el navegador con JavaScript estándar. No necesita servidor, base de datos, API, dependencias ni servicios externos.

### Cómo funciona

1. `src/static/search-index.json` contiene el catálogo indexable: título, URL, descripción, tipo y palabras clave.
2. `src/static/js/search.js` carga ese catálogo y compara la búsqueda ignorando mayúsculas y tildes.
3. Los resultados se ordenan dando más peso al título y a las palabras clave.
4. Los resultados se dibujan con `textContent` y una plantilla HTML, sin insertar contenido como HTML ejecutable.
5. La consulta se conserva en la URL como `/buscar/?q=phishing`.

### Añadir un contenido nuevo al buscador

Al crear una página educativa o un recurso nuevo, añade un objeto a `src/static/search-index.json` con esta estructura:

```json
{
  "title": "Título visible",
  "url": "/ruta-de-la-pagina/",
  "description": "Resumen breve y fiel al contenido.",
  "type": "Área de aprendizaje",
  "keywords": ["sinónimo", "problema habitual", "término técnico"]
}
```

Las palabras clave deben incluir tanto el término técnico como la forma en que una persona normal describiría su problema. Por ejemplo, para phishing: `phishing`, `mensaje raro`, `correo falso`, `enlace sospechoso`. No añadas palabras clave que la página no explique realmente.

### Compilar y validar

Desde la raíz del proyecto:

```bash
python3 -B -m unittest discover -s tests
python3 -B legible/build.py --all
```

La carpeta lista para publicar es `dist/`.
