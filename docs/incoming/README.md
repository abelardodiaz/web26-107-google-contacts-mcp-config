# incoming/ — bandeja de entrada

Aqui aterriza todo lo que llega de **otros proyectos** y aun no esta incorporado al
plan/codigo de este.

## Memos cross-claude

Convencion de nombre:

    NNN-YYYYMMDDHHMMSS-from-claude-X-to-claude-Y-tema.md

- `NNN` = secuencia incremental por proyecto (001, 002, …). No reinicia.
- `YYYYMMDDHHMMSS` = timestamp UTC sin guiones.
- `X`, `Y` = codigos de proyecto (080, 091, 107…).
- `tema` = slug corto en kebab-case.

## Regla de salida

Cuando un memo queda incorporado, se **mueve** a `docs/procesados/`. No se borra: sirve
de auditoria cross-proyecto.
