# Auditoria de seguridad: workspace-mcp 2.0.1 (modo contactos)

- **Paquete:** [`workspace-mcp`](https://pypi.org/project/workspace-mcp/) 2.0.1, de
  [taylorwilsdon/google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp) (MIT)
- **Fecha:** 2026-10-09
- **Alcance:** uso local por stdio con `--tools contacts --single-user`, cuenta @gmail.com personal,
  cliente OAuth propio tipo Desktop.
- **Metodo:** lectura del codigo del wheel publicado, sin ejecutarlo. Tres revisiones en paralelo:
  `auth/`, `main.py` + `core/`, y `gcontacts/`. Despues, instalacion y prueba real en solo lectura.

## Integridad del paquete

| Comprobacion | Resultado |
|---|---|
| sha256 del wheel contra PyPI | `fa5e44ed680730a4be8a1a09b2f4e7fcd176fa944773d5a0a4795405eaa1a3fc`, coincide |
| Publicado | 2026-10-04 17:18 UTC |
| Instalado vs auditado | 91/91 ficheros `.py`/`.yaml` identicos byte a byte |
| Dependencias | 96 paquetes fijados con hash en `requirements.lock`, resolucion congelada al 2026-10-05 |

## Lo que salio limpio

- Con `--tools contacts` solo se importa `gcontacts`; gmail, drive, etc. no se cargan.
- Sin `eval`/`exec`/`pickle`/`__import__`; `subprocess` solo en scripts de publicacion del autor
  (`scripts/release.py`, `scripts/sync_site_docs.py`), que no se ejecutan.
- Destinos de red: solo `accounts.google.com`, `oauth2.googleapis.com` y `people.googleapis.com`.
- Telemetria OpenTelemetry apagada salvo `OTEL_EXPORTER_OTLP_ENDPOINT` + extra `otel` (no instalado).
- OAuth 2.1, proveedor externo, backend GCS y sidecar HTTP: apagados por defecto, cada uno detras
  de una variable de entorno. OAuth 2.1 aborta si se combina con `--single-user`.
- Flujo OAuth con `state` aleatorio de un solo uso y PKCE (S256). Callback solo en loopback.
- Scopes con `--read-only`: `openid`, `userinfo.email`, `userinfo.profile`, `contacts.readonly`.
  Confirmado en la URL real de autorizacion.
- Tokens, refresh token y client secret nunca se escriben en el log. httpx forzado a WARNING.
- Solo se carga un `.env`: el del directorio del paquete en site-packages, no el del CWD.

## Riesgos y mitigacion aplicada

| # | Sev. | Riesgo | Evidencia | Mitigacion |
|---|---|---|---|---|
| 1 | Media | `--read-only` filtra herramientas al arrancar usando un atributo interno de fastmcp (`local_provider._components`). Si una version nueva de fastmcp lo cambia, el filtro devuelve vacio y deja pasar las de escritura sin error. | `core/tool_registry.py:126-136,176-195,237-252` | Dependencias fijadas por hash. `scripts/verificar-mcp.py` falla si aparece algun `manage_*` en modo lectura. Segunda defensa: el token solo tiene `contacts.readonly`. |
| 2 | Media | Requires-Dist solo con `>=`: `uvx workspace-mcp==2.0.1` resolveria dependencias nuevas sin auditar. | METADATA del wheel | Venv propio desde `requirements.lock` con `--require-hashes`. |
| 3 | Media | Refresh token en texto plano, en un JSON junto con el client secret. | `auth/credential_store.py:223-236` | Fichero 0600 (lo crea asi el paquete), directorio 0700 creado por `instalar.sh`, en filesystem Linux nativo. |
| 4 | Baja | Un token con scope `contacts` (escritura) tambien sirve en `--read-only`: anula la segunda defensa del punto 1. | `auth/scopes.py:107,116-135` | Directorios separados `cred-ro/` y `cred-rw/`, uno por wrapper. |
| 5 | Baja | El directorio de credenciales se crea sin `mode` (hereda umask). | `core/utils.py:412` | `instalar.sh` lo crea antes con 0700; los wrappers usan `umask 077`. |
| 6 | Baja | En single-user acepta un callback sin `state` y usa el ultimo guardado. | `auth/google_auth.py:760-778` | Lo frena PKCE (un code ajeno no casa con el verifier). Ventana de 10 min. Aceptado. |
| 7 | Baja | El listener del callback (`localhost:8000-8004`) sigue vivo mientras corre el proceso. | `auth/oauth_callback_server.py:315-337` | Solo loopback; para contactos no sirve nada util. Aceptado. |
| 8 | Baja | `start_google_auth` sigue registrada en modo lectura (no tiene scopes asociados). | `core/server.py:976` | Solo inicia un flujo OAuth con los scopes del modo actual. Aceptado. |
| 9 | Info | El log guarda el email y los `resourceName` de contactos (INFO), crece sin rotacion. | `core/log_formatter.py:193-236` | Fichero 0600 en `~/.contacts-mcp/logs`. Se puede apagar con `WORKSPACE_MCP_STATELESS_MODE=true`. |

## Trampas en escritura (leer antes de activar `run-mcp-rw.sh`)

| Sev. | Trampa | Evidencia |
|---|---|---|
| Alta | `manage_contact` con `address` **borra todas las demas direcciones** y sus campos estructurados: no hay modo merge para direcciones. | `gcontacts/contacts_tools.py:518-519,1033-1034` |
| Alta | `manage_contacts_batch` (update) **reemplaza la lista completa** del campo tocado (un telefono nuevo deja un solo telefono). Los contactos no encontrados se saltan en silencio y el resumen no lo dice. | `contacts_tools.py:1442,1466,1471-1477` |
| Alta | `manage_contacts_batch` (delete) borra hasta 500 contactos sin confirmacion; el mensaje cuenta los pedidos, no los borrados. | `contacts_tools.py:1511,1524-1527` |
| Alta | `manage_contact_group` (delete) con `delete_contacts=True` borra tambien los contactos del grupo. Por defecto es `False`. | `contacts_tools.py:1549,1638` |
| Media | `*_mode="replace"` con lista vacia, `notes=""` o `birthday="clear"` borran el campo. `remove` quita todas las entradas que coincidan. | `contacts_tools.py:396-406,512-525`; `contacts_helpers.py:294-304` |
| Info | No existe "fusionar": la People API no lo ofrece. Fusionar = completar el bueno con `manage_contact` y borrar el duplicado. | — |

Lo que si esta bien hecho: `manage_contact` relee el contacto, usa su etag, reintenta hasta 3 veces
en 412 y solo manda en `updatePersonFields` los campos tocados; el modo por defecto es `merge`.

**Primera fase de escritura:** solo `manage_contact` (por eso `run-mcp-rw.sh` apaga
`manage_contacts_batch` y `manage_contact_group`). Pedir al agente que no use `action=delete`,
`address`, `*_mode="replace"`, `notes=""` ni `birthday="clear"` sin confirmacion caso por caso.
Exportar los contactos desde contacts.google.com antes de empezar.

## No verificado

- Codigo de fastmcp y del resto de dependencias (`google-auth`, `oauthlib`, `uvicorn`): si fastmcp
  lee un `.env` del CWD, que atributos pone en sus spans, como implementa `remove_tool`.
- Comportamiento real de la People API con la `metadata` reenviada al hacer merge.
- Que el wheel corresponda al codigo del repositorio en GitHub.

## Al subir de version

1. Bajar el wheel nuevo sin instalar, verificar sha256 contra PyPI.
2. `diff -r` contra la version auditada; revisar a fondo `auth/`, `core/tool_registry.py`,
   `core/server.py`, `main.py` y `gcontacts/`.
3. Regenerar `requirements.lock` con `--exclude-newer` a una fecha de al menos una semana atras.
4. Instalar y correr `scripts/verificar-mcp.py` en modo lectura.
5. Anotar la version y el resultado en este directorio (`auditoria-workspace-mcp-X.Y.Z.md`).

---

## Anexo 2026-10-21: modulos calendar y drive en --read-only

Para un segundo wrapper (`wrappers/run-mcp-agenda-ro.sh`): leer la agenda y buscar y leer
archivos de Drive de la cuenta personal. Nunca escribir. Misma instalacion 2.0.1, nada nuevo
instalado. Revision del codigo de `gcalendar/`, `gdrive/` y de lo que estos modulos usan de
`auth/` y `core/` de forma distinta a contactos, mas una prueba local solo con `tools/list`
(con un control sin `--read-only` para comprobar que el instrumento distingue los dos modos).

**Filtro.** El mismo que en contactos: `filter_server_tools` quita toda herramienta cuyo scope
no este en `get_all_read_only_scopes()` (`core/tool_registry.py:160-195`, `auth/scopes.py:286-291`).
Con `--read-only` quedan 11 de 24; las 13 de escritura (`manage_event`, `manage_out_of_office`,
`manage_focus_time`, `create_calendar`, `create_drive_folder`, `create_drive_file`,
`import_to_google_*`, `update_drive_file`, `manage_drive_access`, `copy_drive_file`,
`set_drive_file_permissions`) se quitan.

**Scopes con --read-only:** `openid`, `userinfo.email`, `userinfo.profile`,
`calendar.readonly`, `drive.readonly`. Confirmado despues en la URL real de consentimiento.

**Red:** `www.googleapis.com`, `accounts.google.com`, `oauth2.googleapis.com`. Las herramientas
que aceptan URLs o rutas locales (`create_drive_file`, `import_*`, `update_drive_file`) quedan
fuera por el filtro.

| Severidad | Hallazgo | Donde | Mitigacion |
|---|---|---|---|
| Media | El verificador solo buscaba `manage_*`; en Drive las de escritura son `create_*`, `update_*`, `import_*`, `copy_*`, `set_*`. | `scripts/verificar-mcp.py` | Prefijos ampliados y lista blanca exacta para el wrapper agenda (hecho). |
| Media | `get_drive_file_download_url` copia el archivo completo, sin limite, a `/tmp` y a `~/.workspace-mcp/attachments`, fuera del arbol 0700; puede quedarse en disco. | `gdrive/drive_tools.py:578-666`, `core/attachment_storage.py` | `--disabled-tools get_drive_file_download_url`; ademas `WORKSPACE_ATTACHMENT_DIR` y `TMPDIR` dentro de `~/.contacts-mcp`. |
| Media | Contenido de Drive y descripciones de eventos llegan crudos y sin limite; un Doc compartido o una invitacion pueden traer instrucciones, y en la misma sesion hay herramientas que envian correo o comparten. | `gdrive/drive_tools.py:439-444`, `gcalendar/calendar_helpers.py:317` | `WORKSPACE_MCP_MAX_FILE_BYTES=5242880`; envios siempre con confirmacion manual; lo leido es dato, no orden. |
| Baja | Un token con `drive`/`calendar` completos se aceptaria por jerarquia; dos wrappers en el mismo directorio se pisan el token. | `auth/scopes.py:101-135`, `auth/credential_store.py:140-150` | Directorio propio `cred-cal-drive-ro/` (0700). |
| Baja | Los dos wrappers pueden resolver el mismo puerto de callback (8000) y el login de uno falla. | `auth/port_resolver.py`, `auth/oauth_callback_server.py` | `WORKSPACE_MCP_PORT=8010`. |
| Baja | Si el filtro fallara, `create_drive_file`/`import_*` harian la peticion a la URL antes del rechazo de Google. | `gdrive/drive_tools.py:1047-1215` | Lista blanca en el verificador; `WORKSPACE_MCP_DISABLE_LOCAL_FILES=true`. |
| Info | `check_drive_file_public_access` repite permisos y empuja a "compartir con cualquiera". | `gdrive/drive_tools.py:1752-1765` | Apagada con `--disabled-tools`. |

**Lista blanca del wrapper agenda (9):** `get_drive_file_content`, `get_drive_file_permissions`,
`get_drive_shareable_link`, `get_events`, `list_calendars`, `list_drive_items`,
`query_freebusy`, `search_drive_files`, `start_google_auth`.

**Prueba real (2026-10-21):** lista blanca exacta; consentimiento con los dos scopes de lectura;
`list_calendars` OK tras habilitar Calendar API en el proyecto GCP. Drive API pendiente de
habilitar. El verificador daba "LECTURA OK" con un error de API como respuesta: corregido para
que cualquier `Error calling tool` / `API error` sea FALLA.

**No verificado:** a que hosts redirige Google las descargas de `get_media`/`export_media`;
que `build()` no pida el discovery por red; caducidad del refresh token con `drive.readonly`
(scope restringido) si el cliente OAuth estuviera en modo Testing (esta en Produccion).
