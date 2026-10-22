# Changelog

Todos los cambios notables de este proyecto seran documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

---

## [0.2.0] - 2026-10-21

### Added
- `wrappers/run-mcp-agenda-ro.sh`: Google Calendar + Drive en solo lectura, token propio
  (`cred-cal-drive-ro/`), puerto 8010, limite de 5 MB por archivo, sin descargas a disco
  (`--disabled-tools get_drive_file_download_url check_drive_file_public_access`).
- Anexo de auditoria 2026-10-21 para los modulos calendar y drive.

### Fixed
- `scripts/verificar-mcp.py`: detectaba solo `manage_*` como escritura; ahora todos los
  prefijos de escritura y lista blanca exacta para el wrapper agenda.
- `scripts/verificar-mcp.py`: un error de la API ya no se reporta como "LECTURA OK".

## [0.1.0] - 2026-10-09

### Added
- Auditoria de seguridad de `workspace-mcp` 2.0.1 en modo contactos
  (`docs/auditoria-workspace-mcp-2.0.1.md`): integridad, riesgos con mitigacion y trampas
  de escritura.
- `requirements.in` + `requirements.lock`: workspace-mcp 2.0.1 y 96 dependencias fijadas con
  hash, resolucion congelada al 2026-10-05.
- `scripts/instalar.sh`: venv en `~/.contacts-mcp` con `--require-hashes`, directorios 0700.
- `wrappers/run-mcp-ro.sh` (solo lectura) y `wrappers/run-mcp-rw.sh` (solo `manage_contact`),
  con directorios de token separados.
- `scripts/verificar-mcp.py`: cliente JSON-RPC stdio que falla si `--read-only` expone
  herramientas `manage_*`, obtiene la URL de autorizacion y prueba una lectura.
- `PROJECT.yaml`, `CLAUDE.md`, bandeja `docs/incoming/`.
