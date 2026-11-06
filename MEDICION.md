# Medición (GA4) — qué se mide y cómo verificarlo

ConfirMad usa Google Analytics 4 (ID `G-0W7FXLY8XQ`, configurado en `consent.js`).
GA4 **solo se carga después de que alguien acepta las cookies** en el banner de
consentimiento — si rechaza o no decide, no se carga ningún script de Google y no
se manda ningún evento. Todo lo de abajo asume que el visitante ha aceptado.

## Los 6 eventos

| Evento | Cuándo se dispara | Dónde | Parámetros |
|---|---|---|---|
| `select_plan` | Al hacer clic en cualquier botón que lleva a un plan concreto (hero, tarjetas de precio, cierre, página de ejemplo, resultado del chequeo gratuito) | `index.html`, `check.html`, `sample-report.html` | `plan` (`online`/`visit`/`live`), `position` (de dónde vino el clic) |
| `begin_checkout` | Al cargar `solicitar.html` con un plan ya determinado (por la URL o por defecto) | `solicitar.html` | `currency` (`EUR`), `value` (precio numérico), `items` (nombre del plan) |
| `purchase` | Al llegar a `gracias.html` después de pagar, si hay un pedido guardado | `gracias.html` | `transaction_id` (la referencia `CM-...`), `value`, `currency`, `items` |
| `whatsapp_click` | Al hacer clic en cualquier botón o icono de WhatsApp (flotante, cierre de página, fotos del pedido, compartir) | todas las páginas con botón de WhatsApp | `position` (`float`, `closing`, `gracias_photos`, `gracias_share`, etc.) |
| `free_check_result` | Al obtener un resultado en la comprobación gratuita de un anuncio | `check.html` | `risk_level` (`green`/`amber`/`red`), `score` (puntuación interna) |
| `view_sample_report` | Al cargar la página del informe de ejemplo | `sample-report.html` | — |

## Cómo verificarlo en GA4 (DebugView)

1. Entra en GA4 → **Admin** → **DebugView** (o actívalo instalando la extensión
   de Chrome "Google Analytics Debugger", o añadiendo `?gtm_debug=x` no hace
   falta aquí porque GA4 ya manda eventos en tiempo real a DebugView si
   `debug_mode` está activo — más fácil: usa la extensión).
2. Abre confirmad.es en una pestaña con esa extensión activada.
3. Acepta las cookies en el banner (si no lo haces, ningún evento llega).
4. Haz el recorrido de prueba de abajo y comprueba que cada evento aparece en
   DebugView en tiempo real, con los parámetros esperados.

### Recorrido de prueba completo

1. Entra en `/` (home). Haz clic en "Book a visit" del hero → debe verse
   `select_plan` con `plan=visit`, `position=hero`.
2. Vuelve atrás, entra en `/sample-report.html` → debe verse
   `view_sample_report` nada más cargar. Haz clic en "Check a listing" →
   `select_plan` con `plan=visit`.
3. Entra en `/check.html`, rellena el formulario con datos que disparen un
   resultado rojo (por ejemplo: marca "piden pago por transferencia" y
   "piden Western Union") → debe verse `free_check_result` con
   `risk_level=red`. Haz clic en el botón principal del resultado → debe
   verse `select_plan` con `plan=visit`.
4. Eso te lleva a `/solicitar.html?plan=visit` → debe verse `begin_checkout`
   con `value=59.99`, `currency=EUR`.
5. Rellena el formulario y envíalo. Te lleva a Stripe (en producción; en
   pruebas usa el enlace de pago real de Stripe en modo test si lo tienes
   configurado así).
6. Después de "pagar", Stripe debe redirigir a
   `https://confirmad.es/gracias.html` (ver nota pendiente más abajo). Ahí
   debe verse `purchase` con `transaction_id` igual a la referencia
   `CM-YYYYMMDDhhmm-XXXX` que se generó en el paso 5, y `value=59.99`.
7. En `gracias.html`, haz clic en "Send photos on WhatsApp" o en
   "Share on WhatsApp" → debe verse `whatsapp_click`.

Si ves los 6 eventos con los parámetros correctos en ese recorrido,
la medición está funcionando de punta a punta.

### Por qué puede faltar un evento en pruebas

- **No se ve nada:** revisa que aceptaste las cookies — sin consentimiento,
  `window.gtag` nunca se define y ningún evento se manda (es el
  comportamiento correcto, no un fallo).
- **Falta `purchase`:** `gracias.html` solo encuentra la referencia del
  pedido si viene de la misma pestaña/navegador que hizo el checkout
  (usa `sessionStorage`, que no viaja entre dispositivos ni pestañas
  nuevas). Si abres `gracias.html` directamente o desde otro dispositivo,
  verás la página de agradecimiento genérica pero no se disparará
  `purchase` — es la limitación esperada de no tener una base de datos de
  pedidos.
- **`purchase` no se repite al recargar la página:** es intencional, para
  no contar la misma compra dos veces si alguien recarga `gracias.html`.

## Pendiente de tu parte (fuera de este repositorio)

Para que el paso 6 del recorrido funcione en producción, cada uno de los 3
enlaces de pago de Stripe necesita su **redirección después del pago**
apuntando a:

```
https://confirmad.es/gracias.html
```

Esto se configura en el propio enlace de pago de Stripe (Payment Link →
"After payment" → "Redirect customers to another website"), no en este
código — no tengo acceso a tu cuenta de Stripe para hacerlo yo. Si quieres,
puedo escribirte los pasos exactos con capturas de dónde está esa opción en
el panel de Stripe.
