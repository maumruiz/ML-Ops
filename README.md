
# Spike - Desafío ML Engineer

Este repositorio contiene el código para crear un pipeline de entrenamiento de un modelo
para predecir el precio de la leche y crear un API para usar el modelo entrenado.


## Detalles del proceso

Mi forma de abordar el problema fué la siguiente.

### Pipeline

Empecé por dar solución al proceso de pipeline para el código que se nos proporcionó. 
Separé el código que existe en 6 diferentes tareas:

1\) Obtención de datos: En este caso se leen los datos desde archivos csv, 
pero aqui podríamos estar obteniendo datos en tiempo real. Probablemente se necesiten
estar actualizando los datos de precios de la leche, variables climatologicas
y macroeconomicas.

2\) Limpieza de datos: En este paso se limpian todos los datos de variables climatológicas,
variables macroeconómicas y se hace un merge de las 3 fuentes de datos para quedarse con
los features seleccionados para el entrenamiento.

3\) Visualización de datos: Este paso se agrega para monitorear los datos que se limpiaron
en el paso anterior. Se pueden visualizar los datos de precipitaciones y del banco central
a través del tiempo para ciertas regiones y, más importante, se podrían visualizar si hay
outliers en los datos.

4\) Pre-procesamiento: Este paso es dedicado para el pre-procesamiento necesario para
entrenar el algoritmo de regresión. En este caso sólo se separan los datos de entrenamiento
y pruebas, pero se pueden escalar datos, normalizar, etc.

5\) Entrenamiento del modelo: En este paso se entrena un modelo de Ridge Regression para la
predicción del precio de la leche. Se usa GridSearch para buscar los mejores parámetros.

6\) Monitoreo. Este paso es para monitorear los resultados y comportamiento del modelo. Se
deben poder visualizar las métricas obtenidas de nuevos modelos, así como diferentes
gráficas útiles para entender el comportamiento.

![Pipeline](https://raw.githubusercontent.com/maumruiz/ml_challenge/main/pipeline.png?sanitize=true&raw=true)

Para la implementación, mi primer solución fue crear el pipeline con la plataforma de 
[Orchest](https://docs.prefect.io/).  Esta herramienta la encontré en un blog del Linkedin
de Spike, y pienso que es una herramienta demasiado buena porque es muy sencillo crear 
pipelines para ejecutar código de python o jupyter notebooks y crear schedulers para
los pipelines, entre otras cosas...

Una vez separadas las tareas, crear el pipeline fué muy rápido con la
interfaz gráfica de  Orchest, sólo creando cada tarea, asociando el código 
y creando las relaciones del pipeline.

Para acceder al proyecto se puede entrar al siguiente link usando el usuario y 
contraseña que agregué en los comentarios del google form: 
```https://desafio-spike-1d525d52.orchestapp.io/```

Yo no había usando antes Orchest, por lo que al momento de querer crear el API desde 
ahí me di cuenta que no era tan sencillo. No hay mucha documentación y es una herramienta
reciente en evolución. Me topé con el problema de que no iba a ser fácil automatizar el
entrenamiento continuo del modelo y usarlo en una API. Dado el limitado tiempo de 5 horas,
preferí hacer el pipeline manual con código para tener más flexibilidad en la automatización
del deploy para usarlo en la API.

Por lo tanto, mi segunda solución fue usar [Prefect](https://docs.prefect.io/). Esta herramienta
también es fácil de usar para hacer pipelines mediante código, y permite correr
jupyter notebooks. Las moddificaciones que tuve que hacer en los archivos fueron mínimas, pero
tiene algunas diferencias con Orchest: Primero, en Orchest es mucho más sencillo crear los pipelines
y modificar los archivos con su ambiente virtual. Segundo, la comunicación de inputs y outputs son
es muy sencilla en Orchest y en Prefect no. Para Orchest basta con llamar una funcion de la librería
para comunicar datos a través del pipeline. Con Prefect tuve que guardar archivos temporales
para lograr esta comunicación.

Por último, este pipeline se ejecuta al momento de correr y tiene un scheduler con un cron job
para estar ejecutando el pipeline todos los domingos. Para esto asumí la perioricidad para
el pipeline, pero sería cosa de revisar cada cuánto podemos actualizar datos y también del
cliente.

### API

Para crear el API habían un par de cosas que tuve que asumir para el diseño.

Primero, la obtención del modelo podría ser usando siempre la última versión, o ir
actualizando manualmente la versión a utilizar para que primero se verifique que un
modelo actualizado esté funcionando adecuadamente. Aquí decidí usar siempre la última version
del modelo entrenado. 

Segundo, cómo va a funcionar el endpoint de la predicción. Por cómo se realizó el modelo,
se pueden hacer predicciones para cierto mes y año. Asumo que las predicciones se requieren
para un mes próximo o hasta una ventana de meses próximos (no tiene caso hacer predicciones
para meses anteriores). Sin embargo, para hacer la predicción
se necesitan los features de las variables de precipitaciones y banco central, entonces
sólo podemos hacer las predicciones para los meses en los que tenemos estos features.
Por lo tanto, mi solución es guardar los features al momento de limpiar los datos y ponerlos
disponibles para usarlos en el API. El endpoint de la predicción recibe una fecha (mes y año),
revisa si tiene los features y con esto hacer la predicción si hay datos disponibles.

Esto podría mejorar si se pudieran obtener los features en tiempo real para no limitarnos
solamente a los que se tienen disponibles por el momento. También, el modelo debería
poder hacer un time series forecasting, para tener los valores esperados para futuros 
meses, que son los que muy probablemente son los valores que se necesitan.

Para implementar el API utilicé FastAPI. Esta parte fué más rapida que el pipeline ya que 
sólo había que exponer un endpoint para la predicción. El API pide como parámetros el mes
y el año para regresar una predicción. En caso de no tener datos para la predicción, nos
regresa una respuesta de datos insuficientes.

### Servicios

Ya teniendo los procesos de pipeline y el API, encapsulé en contenedores de Docker
cada uno de ellos para tener dos servicios independientes. El contenedor del Pipeline
entrenará el modelo cada cierto tiempo y lo guarda para que el API use la ultima version
disponible para hacer predicciones.

El deploy de estos servicios se logra más fácil ya que los contenedores de Docker tienen
la información necesaria para replicar los resultados en cualquier servidor.


### Monitoreo

Por último, es necesario estar monitoreando todo el proceso para verificar que todo se
esté comportando como se espera. Agregué un paso de monitoreo para visualizar los resultados
de las nuevas versiones del modelo, incluyendo las métricas de RMSE y R2.

Para implementar esto usé la pataforma de [Weights & Biases](https://wandb.ai/) y creé un
proyecto en el que se pueden loggear estadísticas en tiempo real.

Para visualizar el monitoreo se puede entrar a este [link](https://wandb.ai/maumruiz/spike-monitoring).
Dentro de este servicio, podemos ver en la barra lateral todas las ejecuciones del pipeline,
con fecha y hora. Cada una tiene registradas sus métricas y gráficas. En la parte principal
se puede ver el conjunto de métricas registradas para visualizar cómo han ido cambiando
con el tiempo, con nuevas versiones del modelo.
## Estructura del código

El código está organizado de la siguiente manera:

    .
    ├── api                     # Carpeta para el api
    ├── pipeline                # Carpeta para el pipeline
    │   ├── data                # Datos para el modelo
    │   ├── logs                # Logs de resultados de notebooks
    │   ├── models              # Todos los modelos entrenados
    │   ├── tasks               # Tareas del pipeline (notebooks)
    │   └── tmp                 # Archivos temporales
    └── model                   # Último modelo para producción


La carpeta de api contiene la aplicación para exponer un edpoint para consumir predicciones
del modelo.

La carpeta de model contiene la última versión del modelo y los features para las predicciones.

La carpeta de pipeline contiene todos los pasos del pipeline, y se divide en más carpetas.
"data" contiene los datos proporcionados para el challenge, pero los datos se podrían estar
obteniendo de alguna base de datos. "logs" contiene los outputs de los jupyter notebooks de
la última ejecución del pipeline. Estos pueden ser revisados en caso de haber un error o
para monitoreo general del pipeline. "models" es la carpeta donde se guardan todas las versiones
de los modelos entrenados, con la fecha de creación en el nombre del archivo. "tasks" contiene
los archivos de las tareas del pipeline, separados en distintos jupyter notebooks o scripts
de python. "tmp" contiene archivos que se usan para la comunicación entre tareas del pipeline.
Estos archivos se podrían borrar al terminar el pipelione, pero por ahora los estoy dejando ahí.

## Pasos para ejecutar localmente

Para ejecutar el código, se asume que se tiene instalado [Docker](https://docs.docker.com/get-docker/).

El proceso esta compuesto por dos pasos. 

Primero debemos crear la imagen de docker del api 
y del pipeline con los siguientes comandos 
(en la terminal debemos estar en el root del repositorio).

```
docker build -t spike-api ./api
```

```
docker build -t spike-pipeline ./pipeline
```

Lo siguiente es crear dos servicios con las imagenes creadas, 
uno para el api y otro para el pipeline. Estos dos servicios se crean corriendo
el docker-compose que está preparado.

```
docker-compose up -d
```

Con esto tenemos los dos servicios corriendo. Uno con el pipeline 
(con un schedule asignado para correr semanalmente), y otro con el api.


Para comprobar que los contenedores estén corriendo, se puede correr el siguiente comando:

```
docker ps
```

En el cual veremos que están los contenedores spike-api y spike-pipeline corriendo.
Se puede comprobar el API abriendo la dirección ``` localhost:8000 ``` en tu browser, 
y se obtendrá un mensaje de bienvenida.


### Consideraciones

Si es la primera vez que se ejecutan los servicios, el api no va a funcionar hasta
que el pipeline termine su primera ejecución. Esto toma unos cuantos minutos en lo que
se entrena el modelo y se guardan los archivos necesarios.

Una vez que el pipeline haya terminado su primera corrida, veremos archivos creados
en la carpeta model. Con estos archivos creados, ahora si podemos probar el api.


## Documentación del API

#### Healthcheck

Este endpoint se creó para asegurar que el api esta en correcto funcionamiento.
Como respuesta se obtiene un mensaje de bienvenida.

```
  GET /
```

#### Predict

Este endpoint se creó para correr el modelo y hacer una predicción del precio de la leche.
Esta predicción se hace para alguna fecha que esté dentro de los datos recopilados, por lo
que ya tenemos localmente los features para hacer la predicción. Hay dos parámetros
que son el año y la fecha

```
  GET /api/predict/${year}/${month}
```

| Parametro | Tipo     | Descripcion                       | Default     |
| :-------- | :------- | :-------------------------------- | :----------  |
| `year`      | `int` | Año para la predicción |   2020                 |
| `month`      | `int` | Mes para la predicción |    1     |


Ejemplos de llamadas al API:

```
  http://localhost:8000/api/predict?year=2020&month=4
```

```
  http://localhost:8000/api/predict?year=2015&month=4
```

```
  http://localhost:8000/api/predict?year=2014&month=3
```

Las fechas deben ser entre Marzo 2014 y Abril 2020.

## Próximos pasos

Debido al poco tiempo que hay para este desafío, se dejan pendiente 
muchas mejoras al proceso. Algunas de estas son:


- Mandar correo o notificacion cuando falle el pipeline
- Investigar más sobre los pipelines con Prefect para optimizar la comunicación de datos entre tasks.
- Hacer un deploy a producción de los dos servicios con alguna plataforma como Heroku.
- El API no tiene optimizada la carga del modelo. Actualmente cada que se hace una llamada al API, se carga el último modelo existente. Esto podría mejorar cargando en caché el modelo, y en la llamada de la API checar si la versión del caché es la última existente, para no tener que cargar de nuevo el modelo.
- Investigar sobre cómo podría hacer un deploy del modelo desde Orchest para poder usarlo en la API automáticamente.
## Conclusión

En este desafío se crearon dos micro servicios, uno para un pipeline de entrenamiento 
y otro para usar el modelo entrenado por medio de una API.
Sin duda me gustó mas el pipeline con Orchest porque ahí incluso se puede monitorear
fácilmente todo lo que se va entrenando, pero para usarlo tendría que estar moviendo
manualmente los modelos entrenados a los archivos del API. Por esta razón me vi en la necesidad
de usar otro método para el pipeline, con el fin de tener todo completamente automatizado.
El código desarrollado es fácil de ejecutar y se estima que sea fácil de hacer deploy a producción.
Queda pendiente agregar mejoras y optimizar algunas cosas pero con el límite de tiempo se logró
lo necesario para cumplir el desafío.
