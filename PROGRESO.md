# PROGRESO · EDUCA CIBER

## Estado actual
- Rama: `docauto`
- Commit base: `47ed62c`
- Tests: 400 OK
- Build: OK sin avisos
- Prelaunch: ✓ Sin datos de ejemplo

---

## FASE 0 · Fundamentos ⭐ (COMPLETADA)

- [x] 1. `CONTENIDO-GUIA.md` - Guía resumida (§2: reglas, anatomía, checklist, tabla §2.6)
- [x] 2. `src/pages/example/index.html` → Plantilla canónica de lección (noindex)
- [x] 3. Arreglar `phishing/index.html`: anclajes reales en aside + FAQ + 2º quiz-card
- [x] 4. Script `legible/nueva_leccion.py` (modo motor) + probar con lección real

**Hecho cuando:** tests OK, build sin avisos, guía y plantilla creadas, aside de phishing con anclajes reales.

---

## FASE 1 · Fraudes y engaños ⭐ (COMPLETADA)

- [x] 1. `ingenieria-social` — principios de manipulación, desestigmatizar víctima
- [x] 2. `smishing-y-vishing` — SMS/llamadas, familiar en apuros con voz clonada IA, palabra seguridad
- [x] 3. `suplantacion-de-identidad` — perfiles clonados, reducir exposición (defensa)
- [x] 4. `webs-falsas` — HTTPS no garantiza legitimidad, dominio, copia marca
- [x] 5. `enlaces-y-archivos-sospechosos` — acortadores, QR maliciosos, adjuntos, previsualizar
- [x] Extra: enlazar desde recursos/phishing-smishing-vishing/ y recursos/phishing-checklist/ (hecho en lecciones)
- [x] Cierre de hub (`/aprende/fraudes-y-enganos/`): ≥250 palabras, ruta recomendada, quitar noindex

**Hecho cuando:** 5 lecciones reales, hub indexable, tests OK, build sin avisos.

---

## FASE 2 · Contraseñas y cuentas ⭐ (COMPLETADA)

- [x] 1. `buenas-contrasenas` — frases de paso largas y memorables; relleno de credenciales por reutilización
- [x] 2. `gestores-de-contrasenas` — tipos, contraseña maestra, defensa contra phishing
- [x] 3. `verificacion-en-dos-pasos` — SMS vs app autenticadora vs llave física, códigos de recuperación
- [x] 4. `passkeys` — FIDO2/WebAuthn en llano, criptografía clave pública, límites actuales
- [x] 5. `proteger-tus-cuentas-principales` — correo como llave maestra, orden de prioridad, sesiones activas
- [x] 6. `me-han-robado-una-cuenta` — señales compromiso, cierre sesiones, cambio contraseña, recuperación
- [x] Cierre de hub (`/aprende/contrasenas-y-cuentas/`): ruta recomendada, quitar noindex, revisar tarjeta home
- [x] Recursos: `checklist-contrasenas-y-cuentas`, `me-han-robado-una-cuenta-que-hacer`

**Hecho cuando:** 6 lecciones reales, hub indexable, tests OK, build sin avisos.

---

## FASE 3 · Empieza por aquí ⭐ (COMPLETADA)

- [x] 1. `que-es-la-ciberseguridad` — qué protegemos: dinero, identidad, datos, cuentas, dispositivos
- [x] 2. `amenaza-vulnerabilidad-y-riesgo` — analogía doméstica: ladrón, puerta abierta, probabilidad × daño
- [x] 3. `por-que-pueden-atacarme` — cibercrimen automatizado, botnets, superar "no tengo nada interesante"
- [x] 4. `el-factor-humano` — seguridad sin culpa: prisas, cansancio, confianza
- [x] 5. `malware-explicado-sencillo` — virus, troyano, spyware, adware, ransomware; no pagar rescate
- [x] 6. `habitos-basicos-de-seguridad-digital` — decálogo de supervivencia digital enlazado a todas las áreas
- [x] Cierre de hub (`/aprende/empieza-por-aqui/`): quitar noindex, destacar hábitos y qué es ciberseguridad como inicio

**Hecho cuando:** 6 lecciones reales, hub indexable, tests OK, build sin avisos.

---

## FASE 4 · Dispositivos seguros I (COMPLETADA)

- [x] 1. `proteger-tu-ordenador` — principio de menor privilegio: cuenta estándar, antivirus integrado, cortafuegos, copias
- [x] 2. `proteger-tu-movil` — cifrado, bloqueo automático, orígenes desconocidos desactivados, ajustes a revisar
- [x] 3. `actualizaciones` — parches de seguridad vs mejoras estéticas; automáticas; qué pasa con dispositivos sin soporte
- [x] 4. `instalacion-segura-de-aplicaciones-y-permisos` — tiendas oficiales, reseñas, revisión crítica de permisos

**Hecho cuando:** 4 lecciones reales, tests OK, build sin avisos.

---

## FASE 5 · Dispositivos II + Navega I (5 lecciones + cierre hub Dispositivos) (COMPLETADA)

- [x] 1. `bloqueo-y-autenticacion` — PIN vs biometría: ventajas y límites; bloqueo automático
- [x] 2. `wifi-y-bluetooth` — riesgos de redes públicas (MITM explicado sin jerga); VPN cuándo ayuda y cuándo no; Bluetooth
- [x] 3. `perdida-o-robo-del-movil` — IMEI ≠ borrado remoto; antes (localizar, cifrar, copia, IMEI) y después
- [x] 4. `que-significa-https` — certificados TLS/SSL en llano: qué verifican y qué no; candado ≠ web fiable
- [x] 5. `navegadores-y-seguridad` — mito modo incógnito; extensiones, avisos, gestor integrado
- [x] Cierre de hub (`/aprende/dispositivos-seguros/`): quitar noindex, ruta completa (9 lecciones)

**Hecho cuando:** 5 lecciones reales, hub indexable (9 lecciones totales), tests OK, build sin avisos.

---

## FASE 6 · Navega y compra seguro II (5 lecciones + cierre de hub) (COMPLETADA)

- [x] 1. `cookies` — explicación funcional + consentimiento (qué debe poder elegir el usuario)
- [x] 2. `descargas-seguras` — tiendas oficiales vs software pirata (principal vía de malware)
- [x] 3. `comprar-por-internet` — qué debe poder comprobar el comprador: identificación del vendedor, condiciones, política de devoluciones
- [x] 4. `tiendas-fraudulentas` — precios anómalos, pasarelas de pago no estándar, perfiles de anuncio; qué hacer si ya has pagado
- [x] 5. `pagos-online` — tarjetas virtuales de un solo uso; autenticación reforzada (SCA / 3D Secure) en llano; evitar transferencias a particulares
- [x] Cierre de hub (`/aprende/navega-y-compra-seguro/`): enlazar `fraudes/webs-falsas`; activar en hub de Fraudes el enlace "Fraudes en compras online"

**Hecho cuando:** 5 lecciones reales, hub indexable, tests OK, build sin avisos.

---

## FASE 7 · Privacidad e identidad digital (5 lecciones + cierre de hub) (COMPLETADA)

- [x] 1. `privacidad-y-datos-personales` — qué es un dato personal; categorías especiales (salud, biometría) con protección reforzada
- [x] 2. `identidad-digital` — cómo se construye el perfil digital
- [x] 3. `huella-digital-y-reputacion` — egosurfing (buscarte a ti mismo) para detectar exposición; qué es el doxing y cómo reducir riesgo
- [x] 4. `metadatos` — datos ocultos en fotos (ubicación EXIF) y documentos; cómo revisarlos y limpiarlos antes de compartir
- [x] 5. `tus-derechos-sobre-tus-datos` — derechos de acceso, rectificación y supresión ("olvido") y cómo ejercerlos; rol de la AEPD; mención a la cartera de identidad digital europea (eIDAS 2) solo con estado verificado
- [x] Cierre de hub (`/aprende/privacidad-e-identidad/`): fundir los temas del hub (8 → 5) y enlazar "Permisos y privacidad" con la lección de Dispositivos

**Hecho cuando:** 5 lecciones reales, hub indexable, tests OK, build sin avisos.

---

## FASE 8 · Redes sociales y mensajería I (4 lecciones) (COMPLETADA)

- [x] 1. `que-no-publicar` — qué datos evitar compartir (ubicación, documentos, rutinas, menores, metadatos)
- [x] 2. `configuracion-privacidad` — revisar y ajustar visibilidad, etiquetado, apps conectadas, buscadores, mensajería
- [x] 3. `geolocalizacion` — permisos GPS, ubicación precisa vs aproximada, historial, metadatos EXIF, etiquetas de lugar
- [x] 4. `perfiles-falsos` — detectar clonación, reducir exposición, verificar contactos, denunciar suplantación

**Hecho cuando:** 4 lecciones reales, tests OK, build sin avisos, prelaunch OK.

---