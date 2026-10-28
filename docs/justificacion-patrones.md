# Justificación de patrones

## Factory Method

Una respuesta la puede escribir un usuario o un agente de IA. Si Pregunta o Respuesta tuvieran que saber qué tipo de autor es, quedarían atadas a cada tipo y cada vez que aparezca uno nuevo habría que tocarlas.

Por eso hicimos una interfaz Autor que implementan Usuario y AgenteIA, y usamos Factory Method para elegir cuál se pone al crear una respuesta. FabricaAutor es la abstracta, y FabricaAutorHumano y FabricaAgenteIA son las concretas. Pregunta recibe la fábrica en agregarRespuesta(), le pide el autor y crea la Respuesta, sin saber si es humano o IA.

Así Respuesta solo conoce Autor, y si algún día hay otro tipo de autor alcanza con agregar otra fábrica. Una aclaración: las fábricas no crean un autor nuevo cada vez, entregan el usuario que está respondiendo o el agente que ya está registrado.

## Strategy

Para las respuestas automáticas hay que poder usar distintos LLM (OpenAI, Gemini, un modelo local) y cada uno tiene su propia API. Si eso estuviera metido en el dominio, cambiar de proveedor sería complicado y obligaría a modificar el dominio.

Entonces armamos la interfaz EstrategiaLLM con el método generar(prompt) y una clase por proveedor. ServicioRespuestasAutomaticas usa la estrategia que tenga y se puede cambiar con cambiarEstrategia(). La estrategia recibe solo un texto y no una Pregunta, así queda separada del dominio, y para agregar otro proveedor se hace una clase nueva sin tocar nada de lo demás.
