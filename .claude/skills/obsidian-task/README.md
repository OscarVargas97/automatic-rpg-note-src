# /obsidian-task

> Claude Code · skill de proyecto · adaptada del par `obsidian-task`/`obsidian-task-solve` de
> Jueguito a ObsidianRPG el 7 de agosto de 2026.

Convierte un requerimiento en una tarea de **`docs/tareas/`**. Te pregunta el
alcance en un solo intercambio —incluyendo qué segmentos toca, la regla central de
`CLAUDE.md`—, revisa el vault solo lo necesario, y escribe los archivos con tu aprobación. La
tarea enuncia el problema; cómo se resuelve lo decide quien la tome.

| | |
|---|---|
| Destino | `docs/tareas/` |
| Herramientas | `Read` / `Write` / `Grep` / `Glob` sobre el vault local |
| Idioma | español |
| Escribe | solo con aprobación |
| Subagentes | ninguno |

## Diferencia frente a la versión de Jueguito

Sin contrato vault↔GitHub: Jueguito espeja tareas de `Disciplina = Programación` como
issues de GitHub porque ya tiene (o va a tener) un repo de código propio. ObsidianRPG no
tiene repo de implementación todavía (ver `CLAUDE.md` sección 2) — cuando exista, esa pieza
se puede volver a añadir siguiendo el mismo patrón, pero no antes.

## Flujo

Seis pasos: las tareas son el punto de partida del sistema, así que si una tarea *es* crear
una pieza de diseño, un documento o un costo, esa entrada se crea antes que la tarea misma —
el wikilink de la tarea necesita saber el nombre exacto del archivo destino. El tercero es
una compuerta que detiene la ejecución hasta que apruebes.

**01 · Delimitar el alcance preguntando.** El paso principal. Varias preguntas en una sola
llamada a `AskUserQuestion`, con una recomendación primero. La pregunta que nunca falta:
**qué segmentos toca** (`Diseño del sistema`, `Documentación técnica`, `Costos`, `Contexto
para IA`, `Muro de Ideas`, `Ninguno`) — sin esto, nadie sabrá cuándo la tarea está realmente
terminada.

**02 · Investigar solo lo necesario.** Con techo. Busca con `Grep`/`Glob` si ya existe la
nota de diseño, el documento técnico o la fila de costo que la tarea va a tocar, para
enlazarla por wikilink en vez de solo nombrarla.

**03 · Mostrar el borrador en el chat.** Frontmatter y cuerpo de la tarea, y el contenido de
cualquier entrada nueva identificada en el paso 1 — se aprueba todo junto. **Espera
aprobación explícita.**

**04 · Crear primero las entradas nuevas**, si las hay: un `Write` por cada carpeta destino.

**05 · Escribir la tarea** con los wikilinks ya resueltos. El `id` (`TSK-N`) se calcula
localmente en este paso.

**06 · Devolver las rutas**: la tarea y cualquier entrada nueva creada.

## Los límites

| | |
|---|---|
| **0** | subagentes, nunca |
| **1** | tanda de preguntas, sin rondas encadenadas |
| **2** | búsquedas `Grep`/`Glob` en el vault para localizar relaciones, como techo |
| **3** | entradas nuevas creadas en carpetas relacionadas, como techo |

## Convenciones que codifica

**El vault empieza casi vacío.** No asumas que existe una pieza de diseño o un documento
solo porque "tendría sentido que existiera" — verifícalo con `Grep`/`Glob` antes de
referenciarlo.

**Una tarea es un archivo.** `docs/tareas/` no tiene relación padre-hijo ni
sub-items. Si el requerimiento abarca varios frentes, se crean varios archivos hermanos con
`Tema #N — Título`.

**Las `## Referencias` son un punto de partida.** Rutas verificadas, nunca inventadas.

**`segmentos_a_actualizar` y las relaciones son arrays.** Incluso con un solo valor —
escríbelos como lista desde el principio, no como string suelto.

**Nunca asigna `responsable` ni toca `estado`.** Una tarea nueva nace en `Sin empezar`, sin
responsable.

**Sin checkboxes de criterios en el cuerpo.** `definicion_de_hecho` y
`segmentos_actualizados` ya son campos del frontmatter; el cuerpo es prosa.

**Nunca se bloquea esperando respuesta.** Sin respuesta, procede con supuestos declarados en
`## Decisión pendiente`.

**Cierra con la procedencia.** Una línea `Origen:` que permite reconstruir el contexto meses
después.

## Después de publicar

`obsidian-task-solve` es la contraparte: toma la ruta de la tarea escrita, la ejecuta, crea
la rama de convención, y **actualiza ella misma los segmentos declarados** en el vault al
cerrar. Ver `../obsidian-task-solve/README.md`.

## Referencia del vault

Ver `VAULT_MAP.md` en la raíz del repo para las tres tablas de esquema completas (Tareas,
Diseño del Sistema, Documentación Técnica, Costos y Presupuesto), el mapeo de segmentos y el
esquema de IDs — no se duplican aquí para que no puedan divergir.

## Sin scripts

No hay `scripts/` en esta skill: el frontmatter se arma a mano contra las tablas de
`VAULT_MAP.md`. Misma decisión que tomó Jueguito con `obsidian-task` — una sola fuente de
verdad, una lectura por sesión, sin script que la triplique.

## El archivo

La skill vive en `SKILL.md`, junto a este README. El `description` de su frontmatter es lo
que hace que se active sola cuando pidas crear una tarea.

## Dónde está instalada

`<repo>/.claude/skills/obsidian-task/SKILL.md` — vive a nivel de repo, versionada junto a
`CLAUDE.md`, `VAULT_MAP.md` y el propio vault, porque el vault es específico de este
proyecto.

---

Adaptada el 7 de agosto de 2026 del par `obsidian-task`/`obsidian-task-solve` de Jueguito.
Diferencia principal frente a esa versión: sin contrato vault↔GitHub (no aplica — no hay
repo de implementación todavía), taxonomía de `disciplina`/`tipo`/`hito` propia de un
proyecto de especificación de software en vez de un proyecto de videojuego. La regla de
segmentos y el resto de convenciones de `CLAUDE.md` no cambiaron de fondo — solo el
vocabulario del dominio.
