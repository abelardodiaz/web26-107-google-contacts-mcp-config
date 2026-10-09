# google-contacts-mcp-config

Configuracion endurecida del servidor MCP
[`workspace-mcp`](https://github.com/taylorwilsdon/google_workspace_mcp) (taylorwilsdon, MIT)
limitado a **Google Contacts**, corriendo en WSL para usarlo desde Claude Code en Windows.

No es un fork: es el paquete publicado, instalado con dependencias fijadas por hash, mas
wrappers que lo restringen a contactos y separan el token de lectura del de escritura.
Antes de usarlo se audito el codigo: ver
[docs/auditoria-workspace-mcp-2.0.1.md](docs/auditoria-workspace-mcp-2.0.1.md).

```
requirements.in / requirements.lock  -> version fijada (workspace-mcp 2.0.1 + 96 deps con hash)
scripts/instalar.sh                   -> crea ~/.contacts-mcp (0700) y el venv con --require-hashes
wrappers/run-mcp-ro.sh                -> solo lectura (contacts.readonly), token en cred-ro/
wrappers/run-mcp-rw.sh                -> escritura acotada: solo manage_contact, token en cred-rw/
scripts/verificar-mcp.py              -> arranca por JSON-RPC, falla si --read-only expone manage_*,
                                         saca la URL de autorizacion y prueba una lectura
```

## Por que no `uvx workspace-mcp`

El paquete declara sus dependencias solo con `>=`. Con `uvx` cada arranque puede resolver una
version nueva de fastmcp, y el filtro de `--read-only` depende de un atributo interno de fastmcp:
si cambia, el filtro deja pasar las herramientas de escritura sin avisar. Por eso venv propio,
lock con hashes y verificacion despues de cada instalacion.

## Requisitos

- WSL con [uv](https://docs.astral.sh/uv/) y Python 3.12
- Proyecto de Google Cloud con **People API habilitada** y un cliente OAuth tipo **Desktop**
  (puede ser el mismo que ya uses para Gmail). Si la app esta en modo Prueba, los tokens caducan
  a los 7 dias; en Produccion no.

## Instalacion

```bash
bash scripts/instalar.sh
cp wrappers/run-mcp-ro.sh ~/.contacts-mcp/ && chmod 700 ~/.contacts-mcp/run-mcp-ro.sh
# editar las lineas EDITAR: ruta del client OAuth y email
python3 scripts/verificar-mcp.py ~/.contacts-mcp/run-mcp-ro.sh --esperar-auth 600
# abrir la URL que imprime; "app no verificada" -> Avanzado -> Ir a <app>
```

Registro en Claude Code (Windows, scope user):

```bash
claude mcp add --scope user contactos-personal -- wsl /home/USUARIO/.contacts-mcp/run-mcp-ro.sh
```

## Pasar a escritura

Leer antes la seccion "Trampas en escritura" de la auditoria. Exportar los contactos desde
contacts.google.com. Luego instalar `run-mcp-rw.sh` igual que el de lectura (autoriza aparte,
con su propio token) y registrarlo con otro nombre.

Para volver a solo lectura despues de haber autorizado escritura: borrar `cred-rw/` y revocar
el acceso en https://myaccount.google.com/permissions.

## Relacion con otros repos

Mismo patron que `web26-091-gmail-mcp-config` (paquete de terceros + wrappers propios, secretos
fuera del repo).
