#!/bin/bash
# Wrapper MCP Google Calendar + Drive, SOLO LECTURA (agenda del dia y busqueda de archivos).
#
# Mismo venv auditado que run-mcp-ro.sh (scripts/instalar.sh). Los modulos calendar y drive
# se auditaron aparte: docs/auditoria-workspace-mcp-2.0.1.md, anexo 2026-10-21.
# Verificar con lista blanca: python3 scripts/verificar-mcp.py <este wrapper>
#
# Ajustar las dos variables marcadas con EDITAR.
# stdout es el protocolo MCP: no imprimir nada aqui.
B=$HOME/.contacts-mcp
umask 077
mkdir -p "$B/cred-cal-drive-ro" "$B/attachments-cd" "$B/tmp-cd"   # 0700 por el umask
export GOOGLE_CLIENT_SECRET_PATH=$HOME/RUTA/gcp-oauth.keys.json   # EDITAR: client OAuth Desktop
export USER_GOOGLE_EMAIL=USUARIO@gmail.com                        # EDITAR
export WORKSPACE_MCP_CREDENTIALS_DIR="$B/cred-cal-drive-ro"      # token propio, no mezclar
export WORKSPACE_MCP_LOG_DIR="$B/logs"
export WORKSPACE_MCP_BASE_URI=http://localhost                    # callback solo en loopback
export WORKSPACE_MCP_PORT=8010                                    # no chocar con contactos (8000)
export WORKSPACE_MCP_MAX_FILE_BYTES=5242880                       # 5 MB por archivo leido
export WORKSPACE_MCP_DISABLE_LOCAL_FILES=true
export WORKSPACE_ATTACHMENT_DIR="$B/attachments-cd"
export TMPDIR="$B/tmp-cd"
# Las dos apagadas: la primera copia archivos completos a disco; la segunda empuja a compartir
exec "$B/.venv/bin/workspace-mcp" --single-user --tools calendar drive --read-only \
    --disabled-tools get_drive_file_download_url check_drive_file_public_access \
    --transport stdio
