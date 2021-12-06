
# Spike - Desafío ML Engineer

Este repositorio contiene el código para crear un pipeline de entrenamiento de un modelo
para predecir el precio de la leche y crear un API para usar el modelo entrenado.


## Detalles del proceso

Mi forma de abordar el problema fué la siguiente.

### Pipeline

Empecé por dar solución al proceso de pipeline para el código que se nos proporcionó.
Para esto mi primer solución fue crear el pipeline con la plataforma de [Orchest](https://docs.prefect.io/). 
Esta herramienta la encontré en un blog del Linkedin de Spike, y pienso que es una
herramienta demasiado buena porque es muy sencillo crear pipelines para ejecutar código
de python o jupyter notebooks y crear schedulers para los pipelines, entre otras cosas...

Separé el código que existe en 4 diferentes tareas: 1) Obtención de datos,
 2) Limpieza de datos, 3) Pre-procesamiento y 4) Entrenamiento del modelo.

Una vez separadas las tareas, crear el pipeline fué muy rápido con la
interfaz gráfica de  Orchest, solo creando la tarea, asociando el código 
y creando las relaciones del pipeline.

![Pipeline](https://raw.githubusercontent.com/maumruiz/ml_challenge/main/pipeline.png?sanitize=true&raw=true)

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
también es fácil de usar para hacer pipelines mediante código, y permite también correr
jupyter notebooks. Las moddificaciones que tuve que hacer en los archivos fueron mínimas, pero
tiene algunas diferencias con Orchest: Primero en Orchest es mucho más sencillo crear los pipelines
y modificar los archivos con su ambiente virtual. Segundo, los inputs y outputs de orchest
no son tan sencillos como en Prefect. Para Orchest basta con llamar una funcion de la librería
para comunicar datos a través del pipeline. Con Prefect tuve que guardar archivos temporales
para lograr esta comunicación.

### API

Para crear el API utilicé FastAPI. Esta parte fué más rapida que el pipeline ya que sólo
había que exponer un endpoint para la predicción. Por cómo se desarrolló el código y los datos,
me tomé la libertad de asumir que la predicción sería basada en un mes y año, y sólo se podría
predecir para alguna fecha en la que tengamos sus features. Por lo tanto, el API pide como
parámetros el mes y el año para regresar una predicción.

### Servicios

Ya teniendo los procesos de pipeline y el API, encapsulé en contenedores de Docker
cada uno de ellos para tener dos servicios independientes. El contenedor del Pipeline
entrenará el modelo cada cierto tiempo y lo guarda para que el API use la ultima version
disponible para hacer predicciones.

El deploy de estos servicios se logra más facil ya que los contenedores de Docker tienen
la información necesaria para replicar los resultados en cualquier servidor.



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


- El API no tiene optimizada la carga del modelo. Actualmente cada que se hace una llamada al API, se carga el último modelo existente. Esto podría mejorar cargando en caché el modelo, y en la llamada de la API checar si la versión del caché es la última existente, para no tener que cargar de nuevo el modelo.
- Investigar sobre cómo podría hacer un deploy del modelo desde Orchest para poder usarlo en la API automáticamente.
- Investigar más sobre los pipelines con Prefect para optimizar la comunicación de datos entre tasks.
- Hacer un deploy a producción de los dos servicios con alguna plataforma como Heroku.
- Monitorear los resultados del pipeline de entrenamiento.
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
