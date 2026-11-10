# Medición (GA4) — qué se mide y cómo verificarlo

ConfirMad usa Google Analytics 4 (ID `G-0W7FXLY8XQ`, configurado en `consent.js`).
GA4 **solo se carga después de que alguien acepta las cookies** en el banner de
consentimiento — si rechaza o no decide, `window.gtag` nunca se define y no se
manda ningún evento (está probado: no hay errores en consola ni falsos
positivos). Todo lo de abajo asume que el visitante ha aceptado.

## Los 4 eventos de conversión

| Evento | Cuándo se dispara | Dónde | Parámetros |
|---|---|---|---|
| `begin_checkout` | Al hacer **clic** en cualquier botón de reservar un plan (hero, tarjetas de precio, cierre de página, página de ejemplo, botón del resultado del chequeo gratuito) — no al cargar la página de checkout | `index.html`, `check.html`, `sample-report.html` | `plan` (`online`/`visit`/`live`), `value` (precio numérico, con IVA), `currency` (`EUR`), `items` |
| `purchase` | Al llegar a `gracias.html` después de pagar, con `?session_id=...` en la URL | `gracias.html` | `transaction_id` (el `session_id` de Stripe), `value` (con IVA), `currency` (`EUR`), `items` con el plan |
| `free_check` | Al lanzar la comprobación gratuita de un anuncio en `check.html` (al enviar el formulario, o al abrir un enlace compartido que la ejecuta automáticamente) | `check.html` | `risk_level` (`green`/`amber`/`red`), `score` (puntuación interna) |
| `whatsapp_click` | Al hacer clic en **cualquier** enlace de WhatsApp del sitio (botón flotante, pie de página, cierre de página, compartir, fotos del pedido, contacto en el aviso legal) | todas las páginas | `position` (`float`, `footer`, `closing`, `pricing_share`, `gracias_photos`, `gracias_share`, `contact_body`) |

Todo funciona igual en los 4 idiomas (EN, ES, IT, FR): cada versión del sitio
dispara los mismos eventos, con el plan y el precio ya traducidos/convertidos
a número desde el mismo origen de datos que usan los precios visibles.

*(Nota: el sitio también manda `view_sample_report` al cargar la página del
informe de ejemplo — es un extra que ya estaba, no uno de los 4 pedidos, pero
no está de más saber que existe si lo ves en DebugView.)*

## El evento `purchase`, en detalle

Antes, `purchase` dependía de que el navegador aún tuviera guardado en
`sessionStorage` el pedido que se creó justo antes de enviar al cliente a
Stripe — lo cual se rompía si pagaba desde otro dispositivo o con el enlace
reenviado. Ahora usa el **`session_id` real que Stripe añade a la URL de
vuelta**, que funciona siempre, venga de donde venga el clic final de pago:

- Si `gracias.html` recibe `?session_id=...` en la URL (ver sección
  siguiente), usa ese valor como `transaction_id` — así nunca se cuenta dos
  veces el mismo pago, ni siquiera si el cliente recarga la página o vuelve
  a abrir el enlace más tarde (la comprobación de "ya se ha mandado este
  evento" se guarda en `localStorage`, no en `sessionStorage`, así que
  sobrevive a recargas y a cerrar/abrir la pestaña).
- El precio y el nombre del plan los saca de la misma tabla de precios
  canónica que usa el resto del sitio (no un valor escrito a mano), así que
  si cambias un precio en el futuro, `purchase` lo recoge automáticamente
  en el siguiente despliegue.
- Si además el pedido viene de la misma pestaña/dispositivo que hizo el
  checkout (el caso normal), también se le enseña al cliente su propia
  referencia `CM-YYYYMMDDhhmm-XXXX` en la página — pero esa referencia ya
  **no** es lo que se manda a GA4 como `transaction_id`; es solo para que el
  cliente tenga algo legible que anotar o enseñarte si te escribe.

## Lo que tienes que configurar en Stripe (fuera de este repositorio)

Cada uno de tus 3 enlaces de pago necesita su **redirección después del
pago** apuntando a una URL distinta — una por plan, cada una con el plan ya
metido y con el marcador `{CHECKOUT_SESSION_ID}` que Stripe rellena él solo
con el id real de esa compra:

| Plan | Enlace de pago | URL de redirección a configurar |
|---|---|---|
| Online | `.../3cI00d2ty5oB7JfgAaaZi07` | `https://confirmad.es/gracias.html?plan=online&session_id={CHECKOUT_SESSION_ID}` |
| Visita presencial | `.../6oU9AN6JO3gte7DgAaaZi01` | `https://confirmad.es/gracias.html?plan=visit&session_id={CHECKOUT_SESSION_ID}` |
| Visita en directo | `.../4gM3cp6JOeZb9Rn3NoaZi04` | `https://confirmad.es/gracias.html?plan=live&session_id={CHECKOUT_SESSION_ID}` |

Pasos en el panel de Stripe, para cada uno de los 3 enlaces:

1. Entra en **Payment Links** → abre el enlace → **Edit**.
2. Baja hasta **After payment**.
3. Elige **Don't show confirmation page** → **Redirect customers to your
   website**.
4. Pega la URL de la tabla de arriba (la que corresponde a ese plan
   concreto — no uses la misma URL en los 3).
5. Guarda.

No tengo acceso a tu cuenta de Stripe para hacerlo yo; esto es lo único que
queda pendiente de tu lado para que `purchase` funcione en producción con
todos los datos correctos. Hasta que lo configures, `gracias.html` sigue
funcionando (usa como alternativa la referencia que guarda el propio
navegador si el cliente llega desde la misma pestaña), pero sin el
`session_id` real de Stripe.

## Cómo comprobar que cada evento llega a GA4

### Opción A — DebugView (recomendada, la más detallada)

1. Instala la extensión de Chrome "Google Analytics Debugger" y actívala (o
   usa el modo debug de cualquier otra forma que ya tengas configurada).
2. En GA4: **Admin** → **DebugView**.
3. Abre confirmad.es en esa pestaña y **acepta las cookies** en el banner —
   sin esto no se manda nada, es el comportamiento correcto.
4. Haz el recorrido de abajo; cada paso debe aparecer en DebugView en tiempo
   real, con los parámetros indicados.

### Opción B — Informes en tiempo real

**Informes** → **Tiempo real**, sin instalar nada. Es menos detallado que
DebugView (no siempre ves cada parámetro al instante), pero confirma que el
evento llega y con qué nombre.

### Recorrido de prueba completo

1. Entra en `/` (home) y haz clic en "Book a visit" del hero → debe verse
   `begin_checkout` con `plan=visit`, `value=59.99`, `currency=EUR`.
2. Eso te lleva a `/solicitar.html?plan=visit` — comprueba que **no** se
   repite `begin_checkout` al cargar esta página (ya se disparó en el paso
   anterior, al hacer clic).
3. Vuelve a `/check.html`, rellena el formulario con datos que den un
   resultado rojo (por ejemplo: marca "piden pago por transferencia" y
   "piden Western Union") y pulsa el botón de comprobar → debe verse
   `free_check` con `risk_level=red`. Haz clic en el botón principal del
   resultado → debe verse `begin_checkout` con el plan al que te lleva ese
   botón.
4. En cualquier página, haz clic en el icono flotante de WhatsApp (o en
   cualquier otro enlace de WhatsApp que veas: pie de página, "Enviar a
   quien vaya a pagar", etc.) → debe verse `whatsapp_click`.
5. Completa un pago de prueba (en modo test de Stripe) desde `solicitar.html`
   hasta el final. Si ya configuraste la redirección de la tabla de arriba,
   Stripe te devuelve a `gracias.html?plan=...&session_id=cs_test_...` →
   debe verse `purchase` con `transaction_id` igual a ese `session_id`,
   `value` igual al precio del plan, y `currency=EUR`.
6. Recarga `gracias.html` con la misma URL → `purchase` **no** debe volver a
   aparecer (es la protección contra contar el mismo pago dos veces).

Si ves los 4 eventos con los parámetros correctos en ese recorrido, la
medición está funcionando de punta a punta, en los 4 idiomas.

### Por qué puede faltar un evento en pruebas

- **No se ve nada:** revisa que aceptaste las cookies en el banner — sin
  consentimiento, `window.gtag` nunca se define y ningún evento se manda
  (comportamiento correcto, no un fallo).
- **Falta `purchase` o llega sin `session_id` real:** probablemente aún no
  has configurado la redirección de Stripe de la tabla de arriba — mientras
  tanto, `gracias.html` sigue mostrando la página de agradecimiento
  correctamente, pero sin ese dato.
- **`purchase` no se repite al recargar:** es intencional.
