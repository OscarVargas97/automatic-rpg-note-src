# Mapa del vault de ObsidianRPG

Referencia para agentes que trabajan en el vault de gestión de este proyecto. Describe **el
vault de este repo** (tareas, diseño del sistema, documentación técnica, costos) — no
confundir con el esquema que el sistema va a producir para una campaña real, que es un
documento dentro de este mismo vault, no una estructura aparte. Ver la última sección de
`CLAUDE.md` si esto no queda claro.

## Ubicación

`./docs/` — repositorio git aparte (`automatic-rpg-note-docs`), gitignored por este repo
(ver `CLAUDE.md` sección 2). Vive checkoutado ahí en el filesystem, pero no se versiona junto
al resto: sus commits y push se hacen desde dentro de `docs/`, con su propio `git`.

```
docs/
  tareas/                     # Backlog de este proyecto
    terminadas/               # Tareas con estado: Listo — se mueven aquí al cerrarlas
  diseno-del-sistema/         # Especificación del sistema a construir — el entregable central
  documentacion-tecnica/      # Documentación técnica de la implementación (nace vacía)
  costos-y-presupuesto/       # Costos & presupuesto (Whisper local ⇒ probablemente casi vacío)
  meta/
    contexto-para-ia.md       # Contrato de agentes + Log de decisiones
    muro-de-ideas.md
```

## Convención de archivo

El nombre de archivo **es** el título de la nota — los wikilinks `[[Nombre]]` funcionan sin
indirección. El `id` de una tarea (`TSK-N`) vive solo en su frontmatter, nunca en el nombre
de archivo.

**ID siguiente**:
```bash
grep -rho 'id: "TSK-[0-9]*"' docs/tareas/ | grep -o '[0-9]*' | sort -n | tail -1
```
+1. Si el vault está vacío, el primero es `TSK-1`. El frontmatter real es YAML (`id:
"TSK-1"`, sin comillas en la clave) — el patrón busca eso, no un `"id":` con comillas de
JSON.

**Relaciones**: listas de wikilinks en el frontmatter (`["[[Pipeline de ingesta y
enrutamiento]]"]`), apuntando al nombre de archivo en la carpeta correspondiente. No hay
campos de rollup inverso: el panel de backlinks de Obsidian ya los da gratis.

**Tareas terminadas**: cuando `obsidian-task-solve` cierra una tarea con `estado: Listo`, la
mueve de `tareas/` a `tareas/terminadas/` como parte del cierre — el nombre de archivo no
cambia, solo la carpeta. Los wikilinks `[[Tema #N — …]]` siguen resolviendo igual: Obsidian
los resuelve por nombre de archivo en todo el vault, no por ruta. Una tarea nunca se mueve a
mano a `terminadas/` con un `estado` distinto de `Listo`.

**Frontmatter es YAML normal.** Sin script que lo genere: se arma a mano verificando cada
campo select/array contra las tablas de esta sección antes de escribirlo.

## Esquema de propiedades por tipo de nota

### Tareas (`docs/tareas/`)

| Campo | Valores |
|---|---|
| `id` | `TSK-N`, calculado, nunca a mano |
| `titulo` | título de la tarea |
| `estado` | `Sin empezar` \| `En curso` \| `Listo` |
| `tipo` | `Feature` · `Bug` · `Investigación` · `Documentación` · `Admin / Producción` |
| `disciplina` | `Arquitectura del sistema` · `Transcripción y audio` · `Prompt / Ingesta con IA` · `Esquema del vault` · `Documentación` · `Producción` |
| `prioridad` | `P0 - Bloqueante` · `P1 - Alta` · `P2 - Media` · `P3 - Baja` |
| `hito` | `Concepto` · `Especificación` · `Prototipo` · `MVP` · `Piloto en mesa` · `V1` |
| `segmentos_a_actualizar` | array: `Diseño del sistema` · `Documentación técnica` · `Costos` · `Contexto para IA` · `Muro de Ideas` · `Ninguno` |
| `segmentos_actualizados` | bool, todo o nada |
| `definicion_de_hecho` | bool |
| `documentacion_a_actualizar` | array de wikilinks → `docs/documentacion-tecnica/` |
| `diseno_de_referencia` | array de wikilinks → `docs/diseno-del-sistema/` |
| `costo_asociado` | array de wikilinks → `docs/costos-y-presupuesto/` |
| `rama` | texto, vacío hasta que la tarea entra en ejecución |
| `responsable`, `estimacion_dias`, `fechas`, `bloqueada_por` | vacíos salvo dato concreto del usuario |

Cuerpo de la nota (debajo del frontmatter): `## Problema`, `## Resultado esperado`,
`## Decisión pendiente` (si aplica), `## Referencias`, línea `Origen:`.

### Diseño del sistema (`docs/diseno-del-sistema/`)

El entregable central de este repo: cada nota es una pieza de la especificación del sistema
(un esquema, un pipeline, una regla de enrutamiento).

| Campo | Valores |
|---|---|
| `entrada` | nombre de la pieza de diseño |
| `categoria` | `Pipeline de transcripción` · `Ingesta y enrutamiento (Claude)` · `Esquema del vault de campaña` · `Formato de Partidas` · `Interfaz / Flujo de uso` · `Integraciones` · `Otros` |
| `estado` | `Idea` · `Borrador` · `Canon` · `Descartado` — promover a `Canon` exige una fila en el Log de decisiones |
| `prioridad` | MoSCoW, opcional |
| `complejidad` | opcional |

### Documentación Técnica (`docs/documentacion-tecnica/`)

| Campo | Valores |
|---|---|
| `documento` | título |
| `area` | `Transcripción (Whisper)` · `Ingesta y enrutamiento (Claude)` · `Esquema de datos / Frontmatter` · `Vault y escritura de archivos` · `Infraestructura / Despliegue` |
| `estado` | `Vigente` · `Desactualizado` · `Borrador` — nace `Borrador`, nunca `Vigente` de entrada |
| `ruta_en_el_repo` | ruta verificada, vacía si el documento describe algo que aún no tiene implementación |
| `herramientas` | array: `Whisper (local)` · `Claude / Claude Code` · `Python` · `Obsidian` · `Git` · `Otro` |
| `ultima_revision` | fecha |

### Costos (`docs/costos-y-presupuesto/`)

| Campo | Valores |
|---|---|
| `concepto` | nombre del gasto |
| `categoria` | `Software / Licencias` · `Hardware` · `Servidores / Infra` · `Contratistas / Freelance` · `Legal / Admin` |
| `estado` | `Previsto` · `Aprobado` · `Pagado` · `Cancelado` |
| `recurrencia` | `Único` · `Mensual` · `Anual` |
| `proveedor` | opcional |
| `estimado`, `real` | solo si hay una cifra real — nunca inventadas |

## Mapeo de segmentos → ubicación

| Segmento | Dónde |
|---|---|
| `Diseño del sistema` | `docs/diseno-del-sistema/` |
| `Documentación técnica` | `docs/documentacion-tecnica/` |
| `Costos` | `docs/costos-y-presupuesto/` |
| `Contexto para IA` | tabla de Log de decisiones en `docs/meta/contexto-para-ia.md` |
| `Muro de Ideas` | `docs/meta/muro-de-ideas.md` |
| `Ninguno` | no-op |

## Validación local

Este archivo **es** el esquema — no hay script ni copia intermedia. Antes de escribir el
frontmatter de una nota nueva, verifica cada campo select/array contra las tablas de arriba;
si un valor no aparece tal cual, no lo inventes. Ver el `README.md` de
`.claude/skills/obsidian-task/` para el flujo completo.
