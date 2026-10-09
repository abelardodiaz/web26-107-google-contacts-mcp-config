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
escritura = [t for t in tools if t.startswith("manage_")]
if "--read-only" in open(wrapper).read() and escritura:
    p.kill()
    raise SystemExit("FALLA: modo solo lectura expone " + ", ".join(escritura))
print("OK: sin herramientas de escritura" if not escritura else "escritura activa: " + ", ".join(escritura))


def texto(r):
    res = r.get("result") or {}
    return " ".join(c.get("text", "") for c in res.get("content", [])) or json.dumps(r.get("error"))


limite = time.time() + esperar
url_mostrada = False
while True:
    out = texto(rpc("tools/call", {"name": "list_contacts", "arguments": {"page_size": 1}}))
    m = re.search(r"https://accounts\.google\.com/\S+", out)
    if not m:
        print("LECTURA OK (primer contacto omitido por privacidad); longitud respuesta:", len(out))
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
