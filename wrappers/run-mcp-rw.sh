#!/bin/bash
# Wrapper MCP Google Contacts, ESCRITURA ACOTADA (primera fase de mantenimiento).
#
# Solo deja manage_contact (un contacto a la vez, modo merge por defecto).
# Apaga manage_contacts_batch (borra hasta 500 sin confirmar, reemplaza listas
# completas) y manage_contact_group (puede borrar los contactos de un grupo).
# Ver docs/auditoria-workspace-mcp-2.0.1.md, seccion "Trampas en escritura".
#
# Usa un directorio de credenciales DISTINTO al de solo lectura: un token con
# scope `contacts` tambien sirve en --read-only y anularia la segunda defensa.
#
# Antes de usarlo: exportar los contactos desde contacts.google.com.
# stdout es el protocolo MCP: no imprimir nada aqui.
B=$HOME/.contacts-mcp
umask 077
export GOOGLE_CLIENT_SECRET_PATH=$HOME/RUTA/gcp-oauth.keys.json   # EDITAR
export USER_GOOGLE_EMAIL=USUARIO@gmail.com                        # EDITAR
export WORKSPACE_MCP_CREDENTIALS_DIR="$B/cred-rw"
export WORKSPACE_MCP_LOG_DIR="$B/logs"
export WORKSPACE_MCP_BASE_URI=http://localhost
exec "$B/.venv/bin/workspace-mcp" --single-user --tools contacts --transport stdio \
  --disabled-tools manage_contacts_batch manage_contact_group
