# Piloto de selección de modelos con Jev

Banco de pruebas reproducible para comparar tres modelos de OpenRouter en tareas sintéticas y observar qué modelo elegiría Jev. **No integra la selección con Hermes ni activa enrutamiento automático.** Las decisiones de Jev se registran en modo *shadow*: no cambian qué modelos responden.

> Estado: piloto exploratorio con 12 casos. La puntuación formal de las respuestas sigue pendiente; los resultados no validan un enrutador para producción.

## Objetivo

Medir por separado dos cosas:

1. Cómo responden tres modelos a las mismas tareas.
2. Qué modelo recomienda Jev para cada tarea, sin dejar que esa recomendación controle la respuesta.

El mismo conjunto de tres modelos se evalúa en cada caso. Así se evita que el diseño del *track* descarte anticipadamente un candidato. Las descripciones de los modelos son señales generales, no reglas fijas de asignación.

## Modelos y cobertura

| Track de análisis | Casos | Candidatos evaluados por caso |
|---|---|---|
| Alto nivel | H01–H04 | `openai/gpt-6-luna`, `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-flash` |
| Intermedio | M01–M04 | `openai/gpt-6-luna`, `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-flash` |
| Contexto largo | L01–L04 | `openai/gpt-6-luna`, `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-flash` |

La ejecución completa hace 36 llamadas de respuesta (12 casos × 3 modelos) y 12 decisiones de Jev: 48 solicitudes en total. Las solicitudes a modelos y a Jev consumen créditos de OpenRouter.

## Contenido del repositorio

- `cases.json`: casos sintéticos, instrucciones, pistas de selección y rúbricas.
- `fixtures/long_context.md`: expediente industrial ficticio para probar recuperación de contexto y manejo de instrucciones citadas.
- `pilot.py`: comparador opt-in; muestra un plan sin red por defecto.
- `generate_fixture.py`: regenera determinísticamente el expediente y la plantilla de evaluación.
- `retry_failed.py`: reintenta llamadas de modelos fallidas, sin repetir decisiones de Jev ni respuestas exitosas.
- `retry_capped.py`: reintenta respuestas vacías o truncadas por límite de tokens.
- `scorecard.csv`: plantilla vacía con una fila por caso/modelo para puntuar manualmente.
- `results.jsonl`: registro append-only de respuestas, elecciones, latencia, tokens, costos reportados y reintentos de las corridas guardadas.
- `RESULTS.md`: comparación documentada del piloto original y la corrida con cobertura completa.
- `ARTICULO_JEV.md`: artículo de divulgación sobre el origen y el primer piloto; sus cifras describen la corrida inicial, no sustituyen el informe actualizado.

## Requisitos y configuración

- Python 3.10 o posterior.
- Biblioteca estándar de Python; no hay dependencias que instalar.
- Una clave de OpenRouter para ejecutar solicitudes pagadas.

El ejecutor busca `OPENROUTER_API_KEY` primero en el entorno y después en `~/.hermes/.env`. Nunca incluyas una clave en el repositorio ni en `cases.json`.

Ejemplo de configuración solo para la sesión actual:

```bash
export OPENROUTER_API_KEY="<tu-clave>"
```

## Uso

Desde la raíz del proyecto:

```bash
# Regenera fixture y scorecard (operación local)
python3 generate_fixture.py

# Revisa el plan; no llama a APIs ni consume créditos
python3 pilot.py --plan

# Ejecuta todos los casos: 12 decisiones Jev + 36 respuestas de modelos
python3 pilot.py --run
```

Para probar un subconjunto, repite `--case`:

```bash
python3 pilot.py --run --case H01 --case M01 --case L01
```

Este ejemplo hace tres decisiones de Jev y nueve llamadas a modelos. `results.jsonl` se crea si no existe y las nuevas corridas se agregan al final; no se borra el historial. Para revisar salidas incompletas o fallidas:

```bash
python3 retry_failed.py
python3 retry_capped.py
```

El segundo script solo repite la última respuesta de cada par caso/modelo cuando está vacía o terminó con `finish_reason=length`; usa el límite vigente del ejecutor. Ambos reintentos consumen créditos adicionales.

## Evaluación

1. Califica cada respuesta de 1 a 5 con la rúbrica del caso en `cases.json`; evalúa calidad e instrucciones sin conocer el nombre del modelo, si es posible.
2. Registra errores factuales, fidelidad a la evidencia, latencia y costo en `scorecard.csv`.
3. Compara la elección de Jev con el modelo mejor puntuado y mide cuánto pierde la elección frente a ese máximo. Una etiqueta de Jev no es una prueba de que el modelo seleccionado sea el mejor.
4. Repite las decisiones con las mismas opciones e instrucciones para medir estabilidad. Conserva una batería de validación separada de cualquier ajuste de instrucciones.

La batería actual tiene 12 casos sintéticos y una decisión registrada por caso en la corrida corregida. No basta para estimar confiabilidad estadística ni para activar enrutamiento de producción.

## Seguridad, privacidad y límites

Los casos y el expediente incluidos son ficticios. No pegues datos de clientes, credenciales, configuraciones industriales sensibles ni información personal en un benchmark enviado a un proveedor externo sin autorización y anonimización. Este proyecto no ejecuta comandos de control ni modifica una instalación de Hermes.

Las salidas de modelos pueden variar entre ejecuciones. Los costos son los reportados por las respuestas de API, no un estado de facturación de la cuenta. Consulta [`RESULTS.md`](RESULTS.md) para las cifras y limitaciones de las corridas documentadas.
