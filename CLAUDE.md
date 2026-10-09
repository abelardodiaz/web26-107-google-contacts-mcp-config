# CLAUDE.md - Google Contacts MCP Config (web26-107)

## PROJECT.yaml - IMPORTANTE

Este proyecto tiene un archivo `PROJECT.yaml` en la raiz. Es leido por el Project Manager (99999) para monitorear el estado.

**Cuando actualizar:**
- Cambio de version -> actualiza `project.version`
- Siempre actualiza `updated_at` y `updated_by: claude-107`

**NO modificar sin razon:**
- `project.code` - identificador unico
- `server.base_path` - ruta del proyecto (relativa a proposito, repo publico)

---

## Que es este proyecto

Configuracion endurecida de `workspace-mcp` (taylorwilsdon/google_workspace_mcp) limitado a
Google Contacts, en WSL, consumido desde Claude Code en Windows. Paquete de terceros sin fork:
la parte propia son el lock con hashes, los wrappers, el verificador y la auditoria.

## Estructura

```
requirements.in / .lock     -> version fijada con hashes (NO usar uvx)
scripts/instalar.sh         -> venv en ~/.contacts-mcp con --require-hashes
scripts/verificar-mcp.py    -> prueba JSON-RPC; falla si --read-only expone manage_*
wrappers/run-mcp-ro.sh      -> solo lectura, token en cred-ro/
wrappers/run-mcp-rw.sh      -> escritura acotada (solo manage_contact), token en cred-rw/
docs/auditoria-*.md         -> una auditoria por version instalada
PRIVATE-NOTES.md            -> mapeo real de esta maquina (GITIGNORED)
```

## Naturaleza dual: publico + produccion privada

- El **repo es publico**: wrappers genericos con placeholders (`USUARIO`, `RUTA`). Cuenta real,
  rutas reales y proyecto GCP viven en `PRIVATE-NOTES.md`, gitignored.
- La **instalacion real** esta en `~/.contacts-mcp/` de WSL y registrada en Claude Code.

## Politica de seguridad (CRITICA)

- NUNCA commitear tokens, `gcp-oauth*.json`, `client_secret*.json`, `cred-*/`, `logs/` ni
  `PRIVATE-NOTES.md`. El `.gitignore` los bloquea; no lo debilites.
- **Nunca subir de version sin auditar.** Seguir "Al subir de version" en la auditoria vigente.
  Una version nueva de fastmcp puede romper el filtro `--read-only` sin error.
- Despues de cualquier instalacion, correr `scripts/verificar-mcp.py` contra el wrapper ro.
- `cred-ro/` y `cred-rw/` separados siempre: un token de escritura en el directorio de lectura
  anula la segunda defensa.
- Escritura: solo `manage_contact` hasta decidir otra cosa. Ver "Trampas en escritura".

## Convenciones

- Sin emojis en scripts (se corren tambien desde PowerShell).
- Scripts con finales LF; verificar con `file`, no con grep.
- Cambios notables van al `CHANGELOG.md` (Keep a Changelog + SemVer).
