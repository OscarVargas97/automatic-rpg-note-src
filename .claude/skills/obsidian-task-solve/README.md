# /obsidian-task-solve

> Claude Code · skill de proyecto · contraparte de `/obsidian-task` · adaptada del par de
> Jueguito a ObsidianRPG el 7 de agosto de 2026.

Toma la ruta de una tarea de **`docs/tareas/`** y la ejecuta. Se detiene una
sola vez, antes de escribir contenido real, para preguntar lo que la tarea dejó pendiente y
presentar el plan en el mismo mensaje. Crea la rama de convención, ejecuta respetando las
prohibiciones de `CLAUDE.md`, y **al cerrar actualiza ella misma los segmentos declarados**
en el vault — Documentación Técnica, Diseño del Sistema, Log de decisiones — antes de marcar
`segmentos_actualizados` y añadir el registro de cierre al final de la propia tarea. Si el
`estado` queda en `Listo`, además mueve el archivo de la tarea a `tareas/terminadas/`.

| | |
|---|---|
| Entrada | ruta de un archivo en `docs/tareas/` |
| Paradas | una, salvo excepciones duras |
| Git | crea la rama de convención; nunca commitea ni hace push |
| `estado` | lo cambia al cerrar, solo si corresponde |
| Archivo | se mueve a `tareas/terminadas/` si `estado` quedó en `Listo` |
| Subagentes | ninguno |

## La diferencia de fondo con la versión de Jueguito

Jueguito cierra segmentos de un videojuego (código GDScript, mecánicas, documentación
técnica de Godot). Aquí el "producto" de cada tarea suele ser un documento — una pieza de
`diseno-del-sistema/`, una nota de `documentacion-tecnica/` — no código ejecutable, porque
`CLAUDE.md` sección 2 todavía no autoriza código de implementación real en este repo. La
lógica de cierre (segmentos, `segmentos_actualizados`, registro de cierre) es idéntica; lo
que cambia es qué cuenta como "el trabajo".

## La regla que decide qué preguntar

El criterio no es cuánta incertidumbre hay, sino cuánto cuesta deshacer la equivocación —
más una categoría nueva que no es "caro", es **prohibido**:

| Se pregunta (caro) | Se asume | Prohibido — para incluso después de la única parada |
|---|---|---|
| Cambiar el transcriptor elegido | Nombres de archivo, redacción no fijada por el esquema | Escribir código de implementación sin resolver dónde vive |
| Promover una pieza `Canon` a otra cosa | Nivel de detalle de un ejemplo | Inventar lore de ejemplo sin marcarlo ficticio |
| Conflicto real entre `## Resultado esperado` y algo `Canon` | Orden de campos, formato de presentación | — |

Ante la duda de si preguntar: no preguntes. Una corrección sobre un documento ya escrito es
más barata que una ronda de preguntas sobre contenido hipotético. Las prohibiciones, en
cambio, no se resuelven solas ni se preguntan a mitad de camino: paran la ejecución ahí
mismo.

## Flujo

**01 · Leer la tarea y el terreno.** `Read` del archivo completo, `CLAUDE.md` (obligatorio),
los archivos de `documentacion_a_actualizar` (verificando su `estado`), las notas de
`diseno_de_referencia` (si alguna es `Canon`, cambiarla es una prohibición; si es `Idea`
recién creada, se desarrolla aquí).

**02 · Una consulta agrupada, con el plan incluido.** *Única parada.* Preguntas —máximo
cuatro, solo del lado caro o una prohibición que ya se ve venir— y el plan en el mismo
mensaje: hitos, qué pasa con cada segmento declarado, y el nombre de rama que se va a crear.

**03 · Crear la rama.** `feature/TSK-<id>-slug` o `fix/TSK-<id>-slug`, con el `id` tomado del
frontmatter de la tarea. Si el directorio de trabajo todavía no es un repositorio git, para y
pide `git init` — no lo decide por su cuenta.

**04 · Ejecutar completo.** Respeta el esquema de `diseno-del-sistema/Esquema del vault de
campaña.md` si la tarea lo toca. Sin checkpoints salvo prohibiciones. No amplía el alcance:
lo que no está en `## Resultado esperado` se nombra al cerrar como candidato a tarea aparte.

**05 · Actualizar los segmentos declarados.** Edita Documentación Técnica, Diseño del
Sistema, Costos y Presupuesto, el Log de decisiones en `meta/contexto-para-ia.md`, o el Muro
de Ideas según lo que la tarea marcó en `segmentos_a_actualizar`.

**06 · Cerrar.** Marca `definicion_de_hecho` y `segmentos_actualizados` solo si de verdad se
cumplen — todo o nada. Cambia `estado` a `Listo` solo si ambas quedaron ciertas; si no, `En
curso` y lo dice. Un `## Registro de cierre` al final del propio archivo de la tarea.

## Los límites

| | |
|---|---|
| **1** | parada, antes de escribir contenido real |
| **4** | preguntas como techo, en una sola llamada |
| **0** | preguntas también es un resultado válido |
| **1** | comando de git por sesión: `checkout -b`. Nunca commit, nunca push. |
| **1** | registro de cierre por sesión, al final del propio archivo de la tarea |
| **0** | tolerancia a inventar lore sin marcarlo ficticio, cambiar el transcriptor o mover Canon sin fila en el Log de decisiones, o escribir código de implementación sin resolver antes dónde vive |

## Scripts

`scripts/branch_name.py` calcula el nombre de rama (prefijo por `tipo`, slug sin acentos,
largo acotado) de forma determinista. Sin dependencias, solo librería estándar de Python.

## El archivo

La skill vive en `SKILL.md`, junto a este README. El `description` de su frontmatter es lo
que hace que se active sola cuando pases la ruta de una tarea de ObsidianRPG y pidas
resolverla.

## Dónde está instalada

`<repo>/.claude/skills/obsidian-task-solve/SKILL.md` — junto a su contraparte, a nivel de
repo: el vault y el esquema que codifica son específicos de este proyecto.

---

Adaptada el 7 de agosto de 2026 del par `obsidian-task`/`obsidian-task-solve` de Jueguito.
Lo que cambió: sin contrato vault↔GitHub, prohibiciones ajustadas al dominio (transcriptor,
lore ficticio, código de implementación sin territorio decidido) en vez de
Godot/GDScript/addons. La estructura de una sola parada, el registro de cierre y la regla de
segmentos no cambiaron de fondo.
