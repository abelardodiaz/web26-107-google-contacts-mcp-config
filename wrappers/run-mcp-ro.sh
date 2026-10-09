#!/bin/bash
# Wrapper MCP Google Contacts, SOLO LECTURA.
#
# Instalar con scripts/instalar.sh (venv fijado por hash). No usar uvx: resolveria
# dependencias nuevas sin auditar (ver docs/auditoria-workspace-mcp-2.0.1.md).
#
# Ajustar las tres variables marcadas con EDITAR.
# stdout es el protocolo MCP: no imprimir nada aqui.
B=$HOME/.contacts-mcp
umask 077
export GOOGLE_CLIENT_SECRET_PATH=$HOME/RUTA/gcp-oauth.keys.json   # EDITAR: client OAuth Desktop
export USER_GOOGLE_EMAIL=USUARIO@gmail.com                        # EDITAR
export WORKSPACE_MCP_CREDENTIALS_DIR="$B/cred-ro"                 # token solo lectura, separado del rw
export WORKSPACE_MCP_LOG_DIR="$B/logs"
export WORKSPACE_MCP_BASE_URI=http://localhost                    # callback solo en loopback
exec "$B/.venv/bin/workspace-mcp" --single-user --tools contacts --read-only --transport stdio
