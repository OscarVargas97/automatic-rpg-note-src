---
name: obsidian-task-solve
description: Implementa una tarea de docs/tareas/ (vault local de Obsidian de ObsidianRPG) a partir de su ruta. Úsala cuando el usuario pase la ruta de un archivo de esa carpeta y pida resolverla, implementarla, "hazme esta tarea" o "trabajemos esta tarea". Hace una única parada al inicio, crea la rama de convención, ejecuta respetando las prohibiciones de CLAUDE.md, y al cerrar actualiza ella misma los segmentos declarados en el vault (Documentación Técnica, Diseño del Sistema, Log de decisiones), marca segmentos_actualizados + estado, añade el registro de cierre a la propia tarea y, si el estado quedó en Listo, la mueve a tareas/terminadas/.
---

# Resolver tarea del vault (docs/tareas/)

Contraparte de `obsidian-task`: esa crea la tarea sin decidir cómo se resuelve, esta la
ejecuta **y cierra el ciclo completo de segmentos** que `CLAUDE.md` exige — el resultado
declarado en `## Resultado esperado` no cierra la tarea por sí solo; solo
`segmentos_actualizados` marcado en el frontmatter lo hace.

## Principio: una sola parada

Se consulta al usuario **una vez**, antes de empezar a escribir contenido real. Después se
ejecuta completo y sin interrupciones, salvo las excepciones duras de abajo. Una corrección
sobre un documento ya escrito es más barata y más precisa que una ronda de preguntas sobre
contenido hipotético.

### Qué se pregunta y qué se asume

| Se pregunta | Se asume |
|---|---|
| Cambiar el **transcriptor elegido** (Whisper local). | Nombres de archivo, organización interna de una nota. |
| Promover una pieza de `diseno-del-sistema/` marcada **Canon** a otra cosa. | Formato de presentación, redacción de secciones no fijadas por el esquema. |
| Un conflicto real entre `## Resultado esperado` y lo que una pieza **Canon** ya establece. | Orden de campos, nivel de detalle de un ejemplo ilustrativo. |
| Falta un dato real de decisión de producto (p. ej. dónde vivirá el código de implementación) que no está resuelto en `CLAUDE.md`. | Cualquier cosa que ya resuelva `CLAUDE.md` o un vecino equivalente en el vault. |

Ante la duda de si preguntar: no preguntes. Asume, deja el supuesto visible en el reporte
final y en el registro de cierre de la tarea.

### Excepciones duras — no son "caro vs. barato", son prohibiciones

Estas no se asumen ni se resuelven solas: si aparecen, la ejecución se detiene ahí mismo y
se avisa, aunque ya haya pasado la única parada.

- **No se inventa lore de ejemplo sin marcarlo como ficticio.**
- **No se cambia el transcriptor elegido** sin una fila nueva en el Log de decisiones de
  `docs/meta/contexto-para-ia.md` — y eso se pregunta primero, no se decide
  solo.
- **No se promueve una pieza de `diseno-del-sistema/` a Canon** sin la misma fila.
- **No se escribe código de implementación real del sistema** sin que la tarea lo declare
  explícitamente y sin haber resuelto primero dónde vive ese código (`CLAUDE.md` sección 2).

## Entrada

Ruta de un archivo dentro de `docs/tareas/`. Léelo con `Read`. Si lo que se
pasó es una carpeta o un patrón en vez de un archivo concreto, pide cuál tarea antes de
seguir.

## Scripts (léelo antes del flujo — ahorra tokens)

`scripts/branch_name.py` calcula el nombre de rama exacto según `CLAUDE.md` sección 5
(prefijo por `tipo`, slug sin acentos/mayúsculas, largo acotado) — no lo razones a mano, es
un cálculo determinista. El `id` que necesita es el campo `id` del frontmatter de la tarea
(`TSK-N`):

```bash
python3 scripts/branch_name.py --tipo Bug --id 12 --titulo "El esquema no cubre objetos compartidos"
# -> fix/TSK-12-el-esquema-no-cubre-objetos-compartidos
```

## Flujo

### 1. Leer la tarea y el terreno

- `Read` del archivo completo de la tarea: frontmatter y `## Problema`, `## Resultado
  esperado`, `## Decisión pendiente`, `## Referencias`.
- **`CLAUDE.md` del repo — obligatorio.** Es lo que hace innecesaria la mayoría de las
  preguntas: segmentos, convenciones, prohibiciones.
- Los archivos listados en `documentacion_a_actualizar` de la tarea — `Read` de cada uno. Si
  alguno tiene `estado = Desactualizado`, no lo tomes como cierto: verifica y decláralo al
  cerrar. Si tiene `estado = Borrador` y el nombre coincide con la tarea, es probable que
  `obsidian-task` lo haya creado como stub — te toca escribirlo, no crear uno nuevo.
- Las notas listadas en `diseno_de_referencia` — si alguna tiene `estado = Canon`, cambiarla
  cae del lado de las excepciones duras. Si tiene `estado = Idea` y coincide con el nombre de
  la tarea, es el mismo caso: `obsidian-task` ya dio de alta el stub, esta skill lo
  desarrolla.
- Los archivos de `## Referencias` en el cuerpo, verificando que existan.

Sin subagentes.

### 2. Una consulta agrupada, con el plan incluido

Un único mensaje con todo lo necesario:

**Las preguntas** — `AskUserQuestion`, una sola llamada, máximo 4, solo del lado caro de la
tabla o una excepción dura que ya se ve venir. Opciones concretas, consecuencia en la
descripción, recomendación primero.

**El plan, en el mismo mensaje**: hitos con rutas verificadas, qué va a pasar con cada
segmento declarado en `segmentos_a_actualizar`, y el nombre de la rama que se va a crear
(`feature/TSK-<id>-slug` o `fix/TSK-<id>-slug`, según `tipo`).

Si el usuario responde solo las preguntas, el plan queda aprobado por omisión. Si no responde
nada, procede con los supuestos declarados.

### 3. Crear la rama

Antes de escribir contenido real:

1. Verifica que el directorio de trabajo es un repositorio git (`git rev-parse
   --is-inside-work-tree`). Si no lo es, **para** y dile al usuario que falta `git init` — no
   lo decidas por él.
2. Calcula el nombre con `scripts/branch_name.py --tipo <tipo> --id <id> --titulo
   "<titulo>"` y créala con `git checkout -b <resultado>`.
3. **Nunca commitees ni hagas push.** Los cambios quedan en el working tree para revisión;
   crear la rama es la única acción de git que esta skill hace por su cuenta.

### 4. Ejecutar completo

- Sigue el plan. No vuelvas a parar salvo una excepción dura o una bifurcación imprevista del
  lado caro de la tabla.
- Respeta el esquema de `diseno-del-sistema/Esquema del vault de campaña.md` si la tarea lo
  toca — no inventes campos nuevos sin pasar primero por una decisión de diseño.
- Cualquier ejemplo de campaña (Personaje, Lugar, etc.) que escribas para ilustrar algo se
  marca explícitamente como ficticio.
- **No amplíes el alcance.** Lo que no está en `## Resultado esperado` no se hace; lo
  adyacente que valga la pena se nombra al cerrar como candidato a tarea aparte (vuelve a
  entrar por `obsidian-task`).

### 5. Actualizar los segmentos declarados

Esto es lo que cierra la tarea de verdad. Para cada valor presente en
`segmentos_a_actualizar`:

| Segmento | Qué hacer |
|---|---|
| `Documentación técnica` | Edita con `Edit`/`Write` los archivos de `documentacion_a_actualizar` para que reflejen la realidad. Si el área no tenía documento y hacía falta uno, créalo en `documentacion-tecnica/` con `estado = Vigente`. |
| `Diseño del sistema` | Actualiza o crea la nota correspondiente en `diseno-del-sistema/`. Nunca la marques `Canon` sin la fila correspondiente en el Log de decisiones. |
| `Costos` | Actualiza o crea la fila en `costos-y-presupuesto/` solo si hay una cifra real que registrar. No inventes números — si no los tienes, es del lado caro: pregúntalos en el paso 2. |
| `Contexto para IA` | Añade una fila a la tabla de Log de decisiones en `meta/contexto-para-ia.md` si la tarea cambió una convención, el transcriptor elegido, o promovió algo a Canon. Obligatorio si tocaste una excepción dura. |
| `Muro de Ideas` | Actualiza o retira la idea relacionada en `meta/muro-de-ideas.md` si la tarea la resolvió o la descartó. |
| `Ninguno` | Nada que hacer aquí. |

Si un segmento declarado no se pudo actualizar del todo, **no lo marques** y explica por qué
en el registro de cierre. `segmentos_actualizados` es todo o nada.

### 6. Cerrar

- Marca `definicion_de_hecho: true` (frontmatter, con `Edit`) solo si de verdad se cumple.
- Marca `segmentos_actualizados: true` solo si **todos** los segmentos declarados en el
  paso 5 quedaron al día.
- Cambia `estado` a `En curso` si algo del paso 5 quedó pendiente; a `Listo` únicamente si
  `definicion_de_hecho` y `segmentos_actualizados` son ambos ciertos. Nunca lo dejes en
  `Sin empezar`.
- **Si `estado` quedó en `Listo`**, mueve el archivo de la tarea de `tareas/` a
  `tareas/terminadas/` (mismo nombre de archivo, solo cambia la carpeta) — hazlo después de
  escribir el registro de cierre de más abajo, no antes, para no editar un archivo a medio
  mover. Si `estado` quedó en `En curso`, el archivo se queda donde está.
- Resumen en el chat, en este orden:
  1. **Supuestos que tomaste** — lo primero, cada uno con su alternativa en media línea.
  2. Archivos tocados, rama creada.
  3. Segmentos actualizados uno por uno, y cuál quedó pendiente y por qué.
  4. Comandos pendientes de correr a mano (`git commit`, `push`, etc.).
- Añade una sección `## Registro de cierre` al final del propio archivo de la tarea (formato
  abajo), con `Edit`. Uno solo, al final.

## El registro de cierre

```
## Registro de cierre

Ejecutado en la rama <feature/TSK-n-slug>, sin commit todavía.

Decisiones resueltas:
- <decisión tal como aparece en la tarea> → <lo acordado>, porque <razón en media línea>.

Excepciones duras encontradas: <transcriptor / Canon / lore ficticio / código de implementación, si aplicó>.

Segmentos:
- <segmento> → actualizado: <qué cambió>.
- <segmento> → pendiente: <por qué no se pudo>.

Supuestos asumidos: <los que no se consultaron y podrían cambiar>.

Fuera de alcance: <candidatos a tarea aparte con obsidian-task>.

Origen: implementación con <nombre>, <fecha absoluta>.
```

## Límites

| | |
|---|---|
| **1** | parada, antes de escribir contenido real |
| **4** | preguntas como techo, en una sola llamada |
| **0** | preguntas también es un resultado válido |
| **1** | comando de git por sesión: `checkout -b`. Nunca commit, nunca push. |
| **1** | registro de cierre por sesión, al final del propio archivo de la tarea |
| **0** | tolerancia a inventar lore sin marcarlo ficticio, cambiar el transcriptor o mover Canon sin Log de decisiones, o escribir código de implementación sin resolver primero dónde vive |
