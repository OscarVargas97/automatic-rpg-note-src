---
name: obsidian-task
description: Crea una tarea en el vault local de Obsidian de ObsidianRPG (carpeta ObsidianRPG_Obsidian/tareas/) a partir de un requerimiento. Úsala cuando el usuario pida crear una tarea, feature, bug, investigación o pieza de documentación, o diga "genera las tareas asociadas a esto". Delimita el alcance preguntando —incluyendo qué segmentos toca (Diseño del sistema, Documentación técnica, Costos, Contexto para IA, Muro de Ideas) y si crea algo nuevo en esas carpetas—, revisa el vault solo lo necesario, crea como stub y relaciona por wikilink lo que la tarea da origen, y muestra un borrador para aprobación antes de escribir los archivos.
---

# Crear tarea en el vault (ObsidianRPG_Obsidian/tareas/)

## Destino

`ObsidianRPG_Obsidian/tareas/`, dentro del vault local de Obsidian versionado en este repo.
El `id` (`TSK-N`) se calcula escaneando el vault — **nunca lo inventes ni lo pidas al
usuario**. Ver `VAULT_MAP.md` en la raíz del repo para el esquema completo si algo aquí no
cuadra.

## Esquema y validación (léelo antes del flujo — ahorra tokens)

El esquema (valores válidos de `estado`, `tipo`, `categoria`, `area`, etc. en las cuatro
carpetas del vault) vive **solo** en `VAULT_MAP.md`, en la raíz del repo. Si no lo tienes ya
cargado en esta sesión, léelo una vez antes de escribir cualquier frontmatter. No dupliques
esas tablas aquí ni en ningún otro archivo. Arma el YAML a mano, verificando cada campo
select/array contra `VAULT_MAP.md` — si un valor no aparece ahí tal cual, no lo inventes.

**Siguiente ID**: antes de escribir la tarea, calcula el siguiente `TSK-N`. El frontmatter
real es YAML (`id: "TSK-1"`, sin comillas en la clave):

```bash
grep -rho 'id: "TSK-[0-9]*"' ObsidianRPG_Obsidian/tareas/ | grep -o '[0-9]*' | sort -n | tail -1
```

Si no hay resultado, el vault está vacío y el primero es `TSK-1`.

## Flujo

Asistencia, no redacción automática: el alcance lo define el usuario. Siete pasos porque los
pasos 4 y 5 separan "crear lo nuevo" (una pieza de diseño, documento o costo que la tarea da
origen) de "crear la tarea que lo relaciona" — la relación necesita el nombre de archivo
destino ya decidido.

1. **Delimitar el alcance preguntando.** Usa `AskUserQuestion` con **varias preguntas en una
   sola llamada** (hasta 4), nunca una por turno. Elige las que de verdad cambien la tarea,
   con opciones concretas y una recomendación primero. Dimensiones habituales:

   - **Límite del alcance.** Hasta dónde llega este trabajo y qué queda fuera.
   - **Una tarea o varias.** Cada tarea es un archivo independiente en
     `ObsidianRPG_Obsidian/tareas/`, sin jerarquía padre-hijo: si el requerimiento abarca
     frentes separables, crea notas hermanas.
   - **Qué segmentos toca.** *La pregunta que no puede faltar.* Es la regla central del
     proyecto (ver `CLAUDE.md`, sección 3): `Diseño del sistema`, `Documentación técnica`,
     `Costos`, `Contexto para IA`, `Muro de Ideas`, o `Ninguno`.
   - **¿Crea algo nuevo o referencia algo existente?** Cuando el segmento marcado es
     `Diseño del sistema`, `Documentación técnica` o `Costos` y no es obvio del
     requerimiento: ¿esta tarea da de alta una pieza de diseño, un documento técnico o un
     costo que todavía no existe en el vault, o solo toca algo que ya está ahí?
   - **Resultado que la da por terminada.** Qué debe ser observable al cerrarla — un
     documento escrito, un esquema validado, una decisión registrada.
   - **Disciplina, Tipo, Prioridad, Hito** — cuando no sean evidentes del requerimiento.
   - **Casos borde** a incluir o excluir explícitamente.

   Lo que el requerimiento ya responda, no lo preguntes. Si el usuario no contesta, procede
   con supuestos declarados en `## Decisión pendiente` en lugar de bloquear.

2. **Investigar solo lo necesario** (techos exactos en `## Presupuesto`): localiza, si
   aplica, la nota de `diseno-del-sistema/`, el documento de `documentacion-tecnica/` o la
   fila de `costos-y-presupuesto/` que la tarea va a tocar (el vault empieza casi vacío, así
   que hasta que alguna tarea los cree no hay muchos). Es para ubicar y nombrar lo implicado,
   no para resolverlo — eso es trabajo de quien tome la tarea.

3. **Mostrar el borrador en el chat.** Frontmatter y cuerpo de la tarea, en markdown, **y el
   contenido de cualquier entrada nueva** que el paso 1 haya identificado (ver
   `## Entradas nuevas en carpetas relacionadas`) — se aprueba todo junto. Espera aprobación
   explícita.

4. **Crear primero las entradas nuevas**, si las hay: verifica cada campo select contra
   `VAULT_MAP.md` y escríbela con `Write` en la carpeta correspondiente. Guarda los nombres
   de archivo exactos — son los que va a usar el wikilink de la tarea.

5. **Escribir la tarea**: arma el frontmatter verificando cada campo select/array contra
   `VAULT_MAP.md` —combinando lo que ya existía (paso 2) con lo recién creado (paso 4), como
   wikilinks `[[Nombre exacto del archivo]]`— y escríbela con `Write` en
   `ObsidianRPG_Obsidian/tareas/`.

6. **Devolver las rutas**: la del archivo de la tarea y la de cualquier entrada nueva creada.

## Frontmatter

| Campo | Tipo | Qué poner |
|---|---|---|
| `id` | texto | `TSK-N`, calculado en el paso 5. Nunca lo pidas ni lo inventes. |
| `titulo` | texto | Español, infinitivo imperativo. Para lotes de un mismo requerimiento: `Tema #N — Título`, con em dash. |
| `estado` | select | Siempre `Sin empezar`. |
| `tipo` | select | `Feature` · `Bug` · `Investigación` · `Documentación` · `Admin / Producción` |
| `disciplina` | select | `Arquitectura del sistema` · `Transcripción y audio` · `Prompt / Ingesta con IA` · `Esquema del vault` · `Documentación` · `Producción` |
| `prioridad` | select | `P0 - Bloqueante` · `P1 - Alta` · `P2 - Media` · `P3 - Baja` |
| `hito` | select | `Concepto` · `Especificación` · `Prototipo` · `MVP` · `Piloto en mesa` · `V1` |
| `segmentos_a_actualizar` | array | `Diseño del sistema` · `Documentación técnica` · `Costos` · `Contexto para IA` · `Muro de Ideas` · `Ninguno`. **Obligatorio decidirlo, nunca lo dejes vacío por omisión.** |
| `documentacion_a_actualizar` | array de wikilinks | Enlaza el documento si ya existe. Si la tarea da origen a uno nuevo, créalo como stub y enlázalo. |
| `diseno_de_referencia` | array de wikilinks | Enlaza la pieza de diseño si ya existe. Si la tarea crea la pieza, créala como stub y enlázala — nunca la marques `Canon` desde aquí. |
| `costo_asociado` | array de wikilinks | Enlaza la fila si ya existe. Si la tarea es contratar o comprar algo, créala como stub y enlázala — nunca inventes una cifra de `estimado`. |
| `rama` | texto | Vacío. Se rellena cuando la tarea entra en ejecución (`obsidian-task-solve`). |
| `segmentos_actualizados`, `definicion_de_hecho` | bool | No los fijes al crear — nacen en `false`. |
| `responsable`, `estimacion_dias`, `fechas`, `bloqueada_por` | — | Vacíos salvo que el usuario dé un dato concreto (proyecto de una sola persona por ahora). |

`segmentos_a_actualizar`, `documentacion_a_actualizar`, `diseno_de_referencia` y
`costo_asociado` son **arrays** incluso con un solo valor — escríbelos como lista
(`["[[Nombre]]"]`) desde el principio, no como string suelto.

## Entradas nuevas en carpetas relacionadas

Si el requerimiento **es** crear una pieza de diseño, documento técnico o costo, esa entrada
nace aquí como stub — no se espera a la implementación para que exista un rastro
estructurado. Aplica solo cuando el paso 1 estableció que la tarea **crea** el elemento,
nunca cuando solo lo referencia de pasada.

| Carpeta destino | Campos del stub | Nunca fijes |
|---|---|---|
| `diseno-del-sistema/` | `entrada`, `categoria` si es obvia, `estado = Idea` | `estado: Canon` — promoverla exige una fila en el Log de decisiones |
| `documentacion-tecnica/` | `documento`, `area`, `estado = Borrador` | `estado: Vigente` — el documento no existe todavía |
| `costos-y-presupuesto/` | `concepto`, `categoria`, `estado = Previsto`, `recurrencia` si es obvia | `estimado` / `real` — solo si el usuario dio la cifra |

**Orden de escritura:** primero los stubs (paso 4), después la tarea con los wikilinks ya
resueltos (paso 5).

**Techo: 3 entradas nuevas por tarea.** Si el requerimiento implica dar de alta más de tres
cosas en carpetas relacionadas, probablemente son varias tareas, no una tarea con muchos
wikilinks.

## Cuerpo de la tarea

Prosa en español, código inline para identificadores, tablas solo para mapeos reales de
valores. Encabezados, en el orden en que apliquen:

- `## Problema` — qué ocurre hoy y por qué molesta. Máximo 4 líneas.
- `## Resultado esperado` — qué debe ser cierto cuando la tarea esté hecha, en términos
  observables. Sin pasos, sin archivos a modificar, sin decisiones de diseño.
- `## Decisión pendiente` — solo si queda un supuesto real, con su salida alternativa.
- `## Referencias` — lista plana de rutas del vault implicadas que no se pudieron enlazar
  por wikilink. Punto de partida, **no** una lista de trabajo.
- Línea de cierre `Origen: …` con la procedencia: conversación y fecha.

**No decidas la implementación.** Nada de «escribir X para que Y» ni listas de archivos a
tocar: eso lo resuelve quien tome la tarea (`obsidian-task-solve`).

No uses checkboxes ni una sección de "criterios de aceptación" en el cuerpo — esos ya viven
en el frontmatter `definicion_de_hecho` y `segmentos_actualizados`. No repitas el título
dentro del cuerpo.

Una tarea es un archivo. Si el requerimiento pide varios frentes, crea varios archivos
hermanos con la convención `Tema #N — Título`.

## Presupuesto

Preguntar es barato; explorar el vault no. El presupuesto está para que el margen se gaste
en el paso 1.

| | |
|---|---|
| **0** | subagentes, nunca |
| **1** | tanda de preguntas, sin rondas encadenadas |
| **2** | búsquedas `Grep`/`Glob` en el vault para localizar relaciones, como techo |
| **3** | entradas nuevas creadas en carpetas relacionadas, como techo |
| **1** | lectura de `VAULT_MAP.md`, solo si no está ya en contexto de la sesión |

## Después de publicar

`obsidian-task-solve` es la contraparte: toma la ruta de la tarea escrita, la ejecuta, crea
la rama de convención, y al cerrar actualiza ella misma los segmentos declarados en el vault
y marca `segmentos_actualizados` en el frontmatter de la propia tarea. Ver
`../obsidian-task-solve/README.md`.
