# CLAUDE.md

Contexto operativo del proyecto. Léelo entero antes de tocar nada.

---

## 1. Qué es esto

**Este repo es el proyecto real: código en la raíz, más lo necesario para gestionarlo
(`.claude/`, este archivo, `VAULT_MAP.md`).** La documentación y especificación del sistema
viven en `docs/`, un vault de Obsidian versionado como repo aparte (sección 2) — no confundir
las dos cosas.

El sistema que se está construyendo: una mesa de rol (o de creación de lore de un juego) se
graba, un transcriptor de voz la convierte en texto, y Claude procesa esa transcripción para
clasificar automáticamente la información en las notas correspondientes de un vault de
Obsidian — Personajes, Lugares, Facciones, Objetos, Hilos narrativos — y deja un resumen de
la sesión en una nota de Partida. El objetivo es que un máster o un grupo de juego termine
una sesión y tenga el lore actualizado sin transcribir ni ordenar nada a mano.

- **Pitch:** transcripción de voz + Claude → lore de campaña clasificado automáticamente en
  su key correspondiente, con un resumen por partida.
- **Transcriptor elegido:** Whisper local (whisper.cpp / faster-whisper) — ver la fila del
  7 de agosto de 2026 en el Log de decisiones de `docs/meta/contexto-para-ia.md`.
  Sin costo por uso, sin depender de conexión durante la sesión de mesa.
- **Hito actual:** Prototipo — proyecto Django con base de transcripción Whisper local, en la
  raíz de este mismo repo (`config/`, `core/`, `manage.py`, `Makefile`).

Tratar la documentación como desarrollo de software significa: las tareas de `docs/tareas/`
no son "escribir un párrafo de documentación", son unidades de trabajo con alcance, segmentos
que tocan, y una definición de hecho — igual que si el producto fuera código, aunque el
producto de una tarea sea un documento de arquitectura o un esquema de vault.

---

## 2. Territorio: vault vs. código

`docs/` es el vault de Obsidian — la especificación, las tareas, el lore ilustrativo — pero
**no es parte de este repo**: es un repositorio git aparte
(https://github.com/OscarVargas97/automatic-rpg-note-docs), con su propio historial y sus
propias ramas, que simplemente vive checkoutado en la carpeta `docs/` de este directorio.
Este repo lo tiene explícitamente en su `.gitignore` — git nunca lo toca, sin importar en qué
rama de código se esté parado.

Esta es la decisión revisada el 2026-08-07 (reemplaza tanto "un solo repo" como "repos
hermanos sin contenedor" del mismo día): un solo repo hacía que cambiar de rama o rebasear el
código moviera también las notas del vault que Obsidian tiene abiertas, y un submodule
seguiría teniendo el mismo problema — es un puntero versionado que puede divergir entre
ramas. Una carpeta gitignored no puede divergir: siempre es lo que sea que haya en
`docs/` en el filesystem, independiente del commit o rama de este repo. Ver el Log de
decisiones en `docs/meta/contexto-para-ia.md`.

**Los cambios al vault se hacen y se pushean desde dentro de `docs/` directamente** (su
propio `git add`/`commit`/`push` en su propio `main`), nunca a través de una rama de este
repo. Si encuentras un cambio del vault mezclado en un commit de este repo, algo se saltó el
proceso — repórtalo antes de seguir.

---

## 3. La regla central: segmentos

Cada tarea de `docs/tareas/` declara **qué segmentos toca antes de
ejecutarse**:

`Diseño del sistema` · `Documentación técnica` · `Costos` · `Contexto para IA` ·
`Muro de Ideas` · `Ninguno`

Una tarea **no está terminada** hasta que:

1. El resultado declarado en `## Resultado esperado` es observable (un documento escrito,
   un esquema validado, una decisión registrada — según lo que la tarea prometió).
2. Todos los segmentos declarados están actualizados.
3. La casilla **`segmentos_actualizados`** está marcada en el frontmatter de la tarea.

Si durante la ejecución aparece un segmento afectado que nadie previó, **añádelo en ese
momento** y actualízalo. No lo dejes para después.

No hay segmento `Lore` aquí: este proyecto no tiene narrativa propia que proteger — el
"lore" es el dominio del sistema que se está especificando, no de este repo. Tampoco hay
contrato vault↔GitHub como en Jueguito: no hay repo de implementación todavía, así que las
tareas no generan borradores de issue.

---

## 4. Documentación técnica

`docs/documentacion-tecnica/` describe cómo funciona (o funcionará) el
sistema por dentro. Nace vacía — se va llenando tarea por tarea, a medida que se especifican
áreas reales. Áreas esperadas, sin compromiso de que existan todas desde el día uno:

| Área | Cubre |
| --- | --- |
| Transcripción (Whisper) | Cómo se captura audio, configuración del modelo, formato de salida |
| Ingesta y enrutamiento (Claude) | Cómo se lee la transcripción y se decide a qué key va cada fragmento |
| Esquema de datos / Frontmatter | Contrato de campos por tipo de nota — vive primero en `diseno-del-sistema/`, se documenta aquí solo cuando hay implementación real que seguirlo |
| Vault y escritura de archivos | Cómo se crean/actualizan notas sin pisar contenido escrito a mano |
| Infraestructura / Despliegue | Dónde corre el pipeline, requisitos, instalación |

Reglas:

- Si un cambio invalida un documento, **la tarea no está terminada hasta que el documento
  refleje la realidad**. Un documento desactualizado es peor que no tenerlo.
- Si un documento está marcado **Desactualizado**, no confíes en él: verifica y corrígelo.
- Si tu cambio contradice un documento vigente: o ajustas el cambio, o actualizas el
  documento **y** añades una fila al Log de decisiones.

---

## 5. Convenciones que aplican a todo commit

### Ramas y commits

- `main` siempre refleja el estado real del código. Nadie commitea directo sin revisar.
- Ramas: `feature/TSK-12-slug`, `fix/TSK-12-slug` (mismo esquema que Jueguito).
- Commit de código: `verbo en imperativo` normal. Commit dentro de `docs/` (aparte, en su
  propio repo): `[área] verbo en imperativo` — `[esquema] añade campo ultima_mencion a
  Personajes`.
- Este repo es independiente del vault (`docs/`, sección 2): cada uno tiene su propio
  historial, remoto y ramas — y el de `docs/` casi siempre debería ser solo `main`.

### Idioma del código (decisión 2026-08-07, ver Log de decisiones en `docs/`)

- **Código en inglés**: nombres de apps, modelos, campos, vistas, urls, templates, funciones,
  variables, comentarios y docstrings — tanto Python como HTML/templates/JS. Aplica a todo el
  código de este repo (raíz), no a `docs/`.
- **Texto legible para el usuario, en español**: labels, botones, placeholders, mensajes de
  error, help text de comandos — cualquier string que el usuario vea en el navegador o en la
  terminal. La excepción son valores literales atados a un contrato externo ya en español (p.
  ej. los nombres de carpeta `campaña/personajes/` que exige `Esquema del vault de
  campaña.md`) — esos no se traducen porque son datos, no código.
- Ante la duda de si algo es "código" o "texto legible": si el usuario lo lee corriendo la
  app (label, botón, mensaje de error, `--help`), va en español. Si solo lo lee quien edita
  el código (identificador, comentario, nombre de archivo), va en inglés.

### Documentos

- Prosa clara, español, sin relleno. Tablas solo para mapeos reales de valores (frontmatter,
  rutas, decisiones), nunca para narrar.
- Todo documento de `diseno-del-sistema/` o `documentacion-tecnica/` lleva frontmatter según
  `VAULT_MAP.md` — no inventes campos nuevos sin actualizar ese archivo primero.
- Ejemplos ilustrativos de código (snippets de un pipeline, de un prompt) están permitidos
  dentro de un documento de especificación — no cuentan como "código de implementación" para
  la sección 2 mientras no formen un sistema ejecutable real.

---

## 6. Definición de Hecho

- [ ] Cumple el `## Resultado esperado` de la tarea, de forma observable
- [ ] No contradice un documento de `diseno-del-sistema/` marcado `Canon` sin una fila nueva
      en el Log de decisiones
- [ ] Segmentos declarados actualizados
- [ ] Casilla `segmentos_actualizados` marcada en la tarea

---

## 7. Prohibiciones

- **No inventes lore de ejemplo sin marcarlo como ficticio.** Cualquier Personaje, Lugar,
  Facción u Objeto de ejemplo dentro de un documento de especificación necesita decir
  explícitamente que es ilustrativo — nunca se confunde con una campaña real.
- **No cambies el transcriptor elegido** (Whisper local) sin una fila en el Log de
  decisiones de `docs/meta/contexto-para-ia.md`.
- **No promuevas una entrada de `diseno-del-sistema/` a `Canon`** sin la misma fila.
- **No commitees nada dentro de `docs/` a través de este repo.** Está gitignored a propósito
  (sección 2) — los cambios al vault se hacen y se pushean desde dentro de `docs/`
  directamente, con su propio `git`.
- **No cierres una tarea** que tenga segmentos pendientes.

---

## 8. Comandos

Todos vía `Makefile` en la raíz, sobre `uv`:

| Comando | Qué hace |
| --- | --- |
| `make install` | `uv sync` — instala dependencias |
| `make migrate` | `uv run python manage.py migrate` |
| `make makemigrations` | `uv run python manage.py makemigrations` |
| `make run` | `uv run python manage.py runserver` |
| `make shell` | `uv run python manage.py shell` |

---

## 9. Cuando algo no cuadra

Si la tarea es ambigua, si el cambio choca con un documento `Canon`, o si no encuentras la
fuente de verdad de un dato: **pregunta antes de decidir**. Una decisión silenciosa se
convierte en deuda que nadie sabe que existe.

---

## 10. Vault de Obsidian

El mapa completo del vault — estructura de carpetas, esquema de frontmatter por tipo de
nota, mapeo de segmentos — está en [`VAULT_MAP.md`](./VAULT_MAP.md). Consúltalo antes de
crear o editar cualquier nota en `docs/`.

El esquema del vault que el sistema *producirá* para una campaña real (Personajes, Lugares,
Facciones, Objetos, Hilos narrativos, Partidas) es un documento de diseño, no la estructura
de este repo — vive en `docs/diseno-del-sistema/Esquema del vault de
campaña.md`. No lo confundas con `VAULT_MAP.md`, que describe el vault de *este* proyecto.
