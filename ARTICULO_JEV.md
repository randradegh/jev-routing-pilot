# ¿Puede Jev elegir qué modelo responde? Del supuesto a un piloto medible

> Nota de vigencia: este artículo narra el diseño y la primera corrida del piloto, cuando se evaluaron 28 pares modelo/caso. El informe posterior con los tres modelos en todos los casos está en [`RESULTS.md`](RESULTS.md).

## Introducción

La conversación empezó con una pregunta concreta: ¿ya teníamos implementada en Hermes la selección de modelos usando JEV? La diferencia entre “tener acceso a un selector” y “tener un sistema que enruta automáticamente cada solicitud” resultó ser el punto central. Contar con un modelo capaz de clasificar una petición no significa que Hermes ya esté usando esa clasificación para cambiar de modelo. Para saber si la idea estaba lista, había que separar las piezas, comprobar qué estaba disponible y probar la propuesta antes de conectarla al flujo normal de trabajo.

La respuesta fue que todavía no teníamos habilitado un enrutador automático en Hermes. Sí existía la posibilidad de llamar a Jev mediante la capacidad disponible en OpenRouter y desde el skill de modelos de decisión, pero faltaba el componente que toma una decisión y la aplica a la solicitud antes de que el modelo conversacional responda. Por eso, en vez de encender una automatización sin evidencia, acordamos preparar una evaluación en modo *shadow*: Jev clasificaría los casos y registraría qué modelo elegiría, mientras otro modelo produciría la respuesta real.

## Qué hace Jev y qué no hace

Jev, de TypeSafe, es un modelo de decisión estructurada. Se le puede presentar el estado de una solicitud y una pregunta tipada, por ejemplo una selección entre varias opciones. Su respuesta no es un ensayo: devuelve una decisión como una opción elegida, acompañada de probabilidades y confianza. También puede responder preguntas binarias o asignar un puntaje a una escala. Este diseño lo hace útil para clasificación, verificación, ranking o enrutamiento, cuando interesa obtener un resultado que el software pueda procesar directamente [1].

Esa función no equivale a orquestar por sí sola a Hermes. Jev no sustituye el modelo conversacional, no redacta la respuesta final y no cambia automáticamente quién la genera. Para que eso ocurra hace falta integrar su decisión en un punto del flujo de ejecución, definir qué modelos están disponibles y establecer qué hacer si la confianza es baja, falta una respuesta o el servicio no está accesible. La documentación también subraya que Jev devuelve probabilidades, no una explicación en lenguaje natural [1]. En la práctica, eso exige conservar criterios claros y observar sus decisiones, en vez de interpretar una etiqueta como garantía de calidad.

## La propuesta: primero comparar, luego observar el enrutamiento

La evaluación se organizó en dos etapas. Primero compararíamos los modelos por tipo de tarea. Después observaríamos las decisiones de Jev sobre esas mismas tareas, sin permitir que afectara la respuesta. Ese orden ayuda a distinguir dos preguntas que a menudo se confunden: “¿qué modelo respondió mejor?” y “¿Jev supo escogerlo?”. Si ambas se prueban a la vez con enrutamiento activo, un error puede confundirse con el otro.

Para la primera etapa se preparó una batería de doce casos sintéticos: cuatro de alto nivel, cuatro intermedios y cuatro de contexto largo. Cada caso incluye una tarea y una rúbrica para juzgar si la respuesta cumple las instrucciones, evita errores importantes y presenta información suficiente. Se optó por escenarios sintéticos para no enviar conversaciones reales ni datos de clientes al proveedor durante una primera prueba. En los casos industriales también se incorporó evidencia dispersa y algunos registros en conflicto, de modo que la prueba exigiera localizar datos y distinguir decisiones aprobadas de notas históricas o instrucciones citadas.

La segunda etapa fue el modo *shadow*. Jev recibe el caso y registra cuál alternativa seleccionaría, mientras el piloto conserva la respuesta generada por los modelos que se están comparando. Así se puede medir la selección sin alterar el comportamiento visible para el usuario. La propuesta inicial incluía observar calidad según rúbrica, cumplimiento, latencia, costos reportados y uso de herramientas. El piloto no modifica la configuración de Hermes ni activa el enrutamiento: es un banco de pruebas externo y controlado.

## Las herramientas construidas

Para ejecutar el plan se prepararon cuatro artefactos principales. El primero es un catálogo de doce casos con sus rúbricas, separado por tipo de tarea. El segundo es un generador de un expediente industrial ficticio de contexto largo; el generador produce registros ordinarios y entradas especiales que obligan a reconstruir decisiones a partir de varias fuentes internas al mismo expediente. También se añadió una plantilla de puntuación para registrar caso, modelo, evaluación, evidencia, latencia, tokens, costo y elección de Jev.

El cuarto artefacto es el comparador del piloto. En modo de planificación muestra qué modelos y casos se probarían; las llamadas externas requieren una ejecución explícita. Cuando se ejecuta, guarda respuestas, selecciones, latencias y datos de uso en un registro de resultados. Se añadieron reintentos acotados para dos fallos transitorios de conexión y para respuestas que alcanzaron el límite inicial de generación. La documentación del paquete explica el procedimiento y sus límites. Ninguna de estas herramientas constituye todavía una integración de enrutamiento en producción: su propósito es hacer medible la decisión antes de otorgarle control.

## Por qué elegimos esos modelos

La selección acordada buscó equilibrar calidad suficiente, costo y velocidad, no proclamar de antemano un ganador universal. Para tareas de alto nivel —como estructurar una recomendación, comparar alternativas o señalar riesgos y datos faltantes— usamos GPT-6 Luna como candidato principal y DeepSeek V4 Pro como comparación. La hipótesis era reservar Luna para síntesis y juicio de mayor exigencia, y contrastarlo con un modelo de razonamiento sólido para comprobar si la diferencia de respuesta justificaba el costo y el tiempo. OpenRouter describe GPT-6 Luna como una opción eficiente para cargas sensibles a latencia, con capacidad para tareas más complejas al aumentar el esfuerzo de razonamiento [3]. Esa descripción orientó la hipótesis; no reemplaza los resultados del piloto.

Para tareas intermedias incluimos GPT-6 Luna, DeepSeek V4 Pro y DeepSeek V4 Flash. V4 Pro fue la opción de equilibrio que propusimos: suficiente capacidad para instrucciones con varias condiciones, pero con la posibilidad de ser más económico que reservar el modelo de alto nivel para todo. Flash permitió comprobar si tareas rutinarias podían resolverse con menor latencia y costo sin perder precisión. En contexto largo elegimos comparar V4 Pro con V4 Flash. La razón fue que ambos modelos se describen con una ventana de contexto de un millón de tokens, pero Flash está optimizado para eficiencia y rapidez, mientras Pro se orienta a razonamiento avanzado y síntesis de información a gran escala [4][5]. Por eso la prueba podía verificar el compromiso real entre rendimiento, costo y profundidad, en lugar de asumir que un contexto amplio basta para responder bien.

## Qué mostró la primera ejecución

El piloto produjo doce decisiones de Jev y veintiocho respuestas finales de modelos: ocho de GPT-6 Luna, doce de V4 Pro y ocho de V4 Flash. Jev seleccionó GPT-6 Luna en dos casos, V4 Pro en ocho y V4 Flash en dos. Eligió V4 Pro en los cuatro casos intermedios; en las tareas largas dividió sus elecciones entre Pro y Flash. Esto muestra una inclinación clara hacia Pro en esta muestra, pero doce casos son insuficientes para afirmar que ese patrón sea generalizable.

En la revisión cualitativa de las ocho respuestas de contexto largo, ambos modelos recuperaron los datos solicitados y trataron una instrucción maliciosa citada como parte del expediente, no como una orden a seguir. También apareció un punto de atención en una tarea intermedia: la respuesta de V4 Pro rebajó a “pendiente” acciones redactadas como compromisos, mientras GPT-6 Luna y V4 Flash conservaron mejor esa distinción. Como Jev había elegido Pro en los cuatro casos intermedios, este ejemplo ilustra por qué una elección estructurada debe compararse contra resultados, no aceptarse por autoridad.

Las respuestas finales reportaron USD 0.038514 en costos de modelos; sumando las generaciones completadas que luego se reemplazaron durante los reintentos, el registro de costos reportados llega a USD 0.043102. No se guardó el costo de Jev, por lo que esa cifra no representa el gasto total confirmado de la cuenta. La latencia media observada fue de 7.35 segundos para GPT-6 Luna, 26.55 para V4 Pro y 11.70 para V4 Flash. Son promedios de esta batería sintética y de la ruta de proveedor usada en la ejecución; no deben tratarse como garantías de rendimiento futuro. La plantilla para calificación formal por rúbrica quedó disponible, pero todavía no se completó una puntuación ciega y sistemática para todas las respuestas [6].

## Conclusión

La respuesta a la pregunta inicial es precisa: teníamos acceso a Jev y a herramientas para probar decisiones estructuradas, pero no estaba implementada ni activada una selección automática de modelos en Hermes. Se construyó un piloto reproducible para comparar tres modelos en categorías de tarea y medir las elecciones de Jev sin cambiar las respuestas reales. La primera ejecución confirmó que es posible registrar esa señal y ofreció indicios útiles: V4 Pro fue la elección dominante de Jev, Flash respondió bien en contexto largo y hubo al menos una distinción semántica que merece revisión antes de confiar en el selector.

El resultado no es una autorización para desplegar el enrutamiento automático. Es una base para la siguiente etapa: completar la puntuación por rúbrica, ampliar y diversificar los casos, revisar las probabilidades de Jev y acordar un mecanismo de respaldo ante baja confianza o fallos. Así, Hermes podría llegar a seleccionar modelos con evidencia y límites explícitos, en vez de convertir una capacidad disponible en una automatización prematura.

## Bibliografía

1. OpenRouter. “Jev Documentation: Using the TypeSafe Decision Model on OpenRouter.” https://openrouter.ai/docs/guides/community/jev
2. OpenRouter. “Submit a Decisions request.” https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request
3. OpenRouter. “OpenAI: GPT-6 Luna.” https://openrouter.ai/openai/gpt-6-luna
4. OpenRouter. “DeepSeek V4 Pro.” https://openrouter.ai/deepseek/deepseek-v4-pro
5. OpenRouter. “DeepSeek V4 Flash.” https://openrouter.ai/deepseek/deepseek-v4-flash
6. Piloto interno Jev Routing, “Resultados del piloto” y registros de ejecución (`RESULTS.md`, `results.jsonl`), artefactos locales preparados para esta evaluación.
