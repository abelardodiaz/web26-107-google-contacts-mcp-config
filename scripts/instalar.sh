#!/bin/bash
# Instala workspace-mcp en ~/.contacts-mcp/.venv desde requirements.lock (con hashes).
#
# Uso: bash scripts/instalar.sh
# Requiere uv (https://docs.astral.sh/uv/). Debe correr en un filesystem Linux
# nativo: en /mnt/c (DrvFs) los chmod no tienen efecto.
#
# Para subir de version: editar requirements.in, regenerar el lock con
#   uv pip compile requirements.in --generate-hashes --python-version 3.12 \
#     --exclude-newer <fecha> -o requirements.lock
# y repetir la auditoria antes de instalar (ver docs/).
set -euo pipefail
REPO=$(cd "$(dirname "$0")/.." && pwd)
B=$HOME/.contacts-mcp
UV=${UV:-$(command -v uv || echo "$HOME/.local/bin/uv")}
umask 077
mkdir -p "$B/cred-ro" "$B/cred-rw" "$B/logs"
chmod 700 "$B" "$B/cred-ro" "$B/cred-rw" "$B/logs"
"$UV" venv --python 3.12 -q "$B/.venv"
"$UV" pip sync --python "$B/.venv/bin/python" --require-hashes "$REPO/requirements.lock" -q
"$B/.venv/bin/workspace-mcp" --help >/dev/null && echo "instalado: $("$B/.venv/bin/python" -c 'import importlib.metadata as m; print(m.version("workspace-mcp"))')"
echo "Siguiente: copiar wrappers/*.sh a $B, editar las lineas EDITAR y correr scripts/verificar-mcp.py"
