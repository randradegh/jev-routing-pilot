# Resultados del piloto Jev

## Resumen

El piloto compara 12 casos sintéticos con tres candidatos por caso. La decisión de Jev se registra en modo *shadow*: no controla qué modelo genera las respuestas. La batería continúa siendo exploratoria; el `scorecard.csv` no tiene puntuaciones manuales completas y no se ha validado el enrutamiento para producción.

## Corrida inicial: 28 pares modelo/caso

La primera matriz evaluó 28 respuestas modelo/caso: GPT-6 Luna en 8, DeepSeek V4 Pro en 12 y DeepSeek V4 Flash en 8. Jev registró 12 decisiones y eligió GPT-6 Luna en 2 casos, V4 Pro en 8 y V4 Flash en 2.

**Aclaración metodológica:** Jev ya recibía los tres candidatos globalmente en esa corrida; `cases.json` limitaba cuáles respuestas de modelo se generaban y comparaban en algunos *tracks*. Por tanto, las elecciones iniciales no estaban restringidas al subconjunto de `cases.json`, pero sí faltaban respuestas de ocho combinaciones modelo/caso: Flash en H01–H04 y Luna en L01–L04.

La corrida incluyó reintentos por fallos transitorios y por respuestas limitadas por el máximo inicial de tokens. El costo reportado de las respuestas finales fue USD 0.038514; al sumar generaciones reemplazadas, USD 0.043102. El costo de Jev no quedó registrado en esa corrida, así que esas cifras no son el gasto total de la cuenta.

## Corrida corregida: tres modelos en cada caso

Se evaluaron los tres modelos en cada uno de los 12 casos: **36 respuestas de modelo y 12 decisiones de Jev**. Dos respuestas llegaron al límite de 2,400 tokens y se repitieron con un límite de 3,600; ambas terminaron con `finish_reason=stop`. No hubo errores sin recuperar en el conjunto de respuestas final.

| Modelo elegido por Jev | Corrida inicial | Corrida corregida |
|---|---:|---:|
| `openai/gpt-6-luna` | 2 | 3 |
| `deepseek/deepseek-v4-pro` | 8 | 3 |
| `deepseek/deepseek-v4-flash` | 2 | 6 |

La elección cambió en 9 de los 12 casos. No debe atribuirse ese cambio a la ampliación de `cases.json`: Jev ya recibía los tres candidatos antes. Para la corrida corregida también se neutralizaron las descripciones e instrucciones de selección que asociaban modelos con categorías de tarea; además, se hizo una nueva llamada a Jev. No se aisló experimentalmente el efecto de esos cambios ni la variación entre ejecuciones.

La primera pasada de la corrida corregida reportó USD 0.069886 para llamadas a modelos y USD 0.000323 para Jev (USD 0.070209 en conjunto). Ese subtotal no incluye el costo de las dos respuestas repetidas; el costo total de la corrida corregida no quedó conciliado. No comparar este subtotal directamente con los costos de la corrida inicial, que no incluyen Jev.

La nueva cobertura permite comparar los ocho candidatos antes ausentes, pero no hay una puntuación ciega completa de calidad. En consecuencia, no se concluye que las nuevas elecciones sean más correctas ni que un modelo sea superior en general.

## Métricas y límites

- La muestra contiene 12 casos sintéticos; la calidad no se ha calificado formalmente con la rúbrica.
- Una sola elección por caso no permite medir estabilidad o calibración de Jev.
- Los cambios de instrucciones y la variación de una nueva corrida impiden atribuir causalmente los cambios de selección a una sola variable.
- `results.jsonl` conserva los registros históricos, corridas nuevas y reintentos. Al reconstruir una respuesta final, usar la última respuesta exitosa para cada par caso/modelo.
- Ninguna corrida activa el enrutamiento automático de Hermes.
