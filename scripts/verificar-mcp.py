#!/usr/bin/env python3
"""Arranca el MCP por stdio (JSON-RPC directo), lista herramientas y prueba una lectura.

Uso: python3 verificar-mcp.py /ruta/al/wrapper.sh [--esperar-auth SEGUNDOS]

- Falla si en modo solo lectura aparece alguna herramienta manage_*.
- Llama list_contacts con page_size=1. Si falta autorizacion, imprime la URL
  y reintenta cada 10 s hasta que el usuario autorice o se acabe el tiempo.
"""
import json
import re
import subprocess
import sys
import time

wrapper = sys.argv[1]
esperar = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--esperar-auth" else 0

p = subprocess.Popen(["bash", wrapper], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=open("/tmp/verificar-mcp.stderr", "w"), text=True, bufsize=1)
_id = 0


def rpc(method, params=None, notify=False):
    global _id
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if not notify:
        _id += 1
        msg["id"] = _id
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    if notify:
        return None
    while True:
        line = p.stdout.readline()
        if not line:
            raise SystemExit("ERROR: el servidor cerro stdout (ver /tmp/verificar-mcp.stderr)")
        r = json.loads(line)
        if r.get("id") == _id:
            return r


rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "verificar-107", "version": "0.1"}})
rpc("notifications/initialized", notify=True)
tools = [t["name"] for t in rpc("tools/list")["result"]["tools"]]
print("herramientas:", ", ".join(sorted(tools)))
contenido = open(wrapper).read()
# Prefijos de escritura de todos los modulos (en Drive no se llaman manage_*: anexo 2026-10-21)
ESCRITURA = ("manage_", "create_", "update_", "import_", "copy_", "set_", "delete_", "modify_", "send_")
escritura = [t for t in tools if t.startswith(ESCRITURA)]
if "--read-only" in contenido and escritura:
    p.kill()
    raise SystemExit("FALLA: modo solo lectura expone " + ", ".join(escritura))
# Lista blanca por wrapper: cualquier herramienta fuera de la lista es falla, aunque no
# tenga prefijo de escritura (un prefijo nuevo no pasaria el filtro de arriba)
if "--tools calendar drive" in contenido:
    esperadas = {"get_drive_file_content", "get_drive_file_permissions", "get_drive_shareable_link",
                 "get_events", "list_calendars", "list_drive_items", "query_freebusy",
                 "search_drive_files", "start_google_auth"}
    if set(tools) != esperadas:
        p.kill()
        raise SystemExit("FALLA: herramientas distintas a la lista blanca. Sobran: "
                         + ", ".join(sorted(set(tools) - esperadas)) + " | faltan: "
                         + ", ".join(sorted(esperadas - set(tools))))
    prueba = ("list_calendars", {})
else:
    prueba = ("list_contacts", {"page_size": 1})
print("OK: sin herramientas de escritura" if not escritura else "escritura activa: " + ", ".join(escritura))


def texto(r):
    res = r.get("result") or {}
    return " ".join(c.get("text", "") for c in res.get("content", [])) or json.dumps(r.get("error"))


limite = time.time() + esperar
url_mostrada = False
while True:
    out = texto(rpc("tools/call", {"name": prueba[0], "arguments": prueba[1]}))
    m = re.search(r"https://accounts\.google\.com/\S+", out)
    # Un error de la API no es una lectura (2026-10-21: "Calendar API is not enabled" salia como OK)
    if not m and re.search(r"Error calling tool|API error|is not enabled|\"code\":", out):
        p.kill()
        raise SystemExit("FALLA en la lectura: " + out[:300])
    if not m:
        print(f"LECTURA OK con {prueba[0]} (contenido omitido por privacidad); longitud respuesta:", len(out))
        print(out.splitlines()[0] if out else "")
        break
    if not url_mostrada:
        print("AUTORIZAR EN:", m.group(0).rstrip(").,'\""), flush=True)
        url_mostrada = True
    if time.time() > limite:
        print("Sin autorizacion dentro del tiempo de espera.")
        break
    time.sleep(10)
p.kill()
