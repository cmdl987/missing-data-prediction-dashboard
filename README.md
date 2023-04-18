# __Final Project - Missing data prediction and temperature monitoring.  [EN] / [[ES]](#proyecto-final-predicción-de-datos-faltantes-y-monitorización-de-temperatura-es)__
The code in this repository was created between September and October 2022, for the final project within the _Python Programming Course_ offered by Madrid's Employment Agency in collaboration with a number of companies belonging to [**Clúster Big Data Madrid**](https://www.bigdatamadrid.org/). 

The planning, development and execution of the code was carried out by: 
- Cristóbal Moreno (@cmdl987) [![GitHub](https://i.stack.imgur.com/tskMh.png) GitHub](https://github.com/cmdl987)     | [![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/cmorenodel/)
- Alex Fuller (@AlexFul) [![GitHub](https://i.stack.imgur.com/tskMh.png) GitHub](https://github.com/AlexFul) | [![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/alex-fuller-7833031/)





-----
## __Contents:__
1. [Project objectives](#1--project-objectives)
2. [Disclaimer](#2--disclaimer)
3. [Libraries used](#3--libraries-used)
4. [Development steps](#4--development-steps)
    
    4.1. [Data Analysis](#41-data-analysis)

    4.2. [Machine Learning (Prophet)](#42-machine-learning-prophet-model)

    4.3. [Visualisation](#43-visualisation)

    
5. [Installation](#5--installation)
6. [Code implementation](#6--code-implementation)

-----


## __1.- Project objectives.__


a) **Create a model capable of using historic data to predict values of missing data.** The data comes from temperature tracking sensors in vehicles transporting food and pharmaceuticals.

b)  **Visualize the results in an interactive dashboard** using the Dash library, with the following main KPIs:

- Time series graphs with 5 minute intervals showing both real temperature and estimated missing data, each in a different colour.
- Missing data as a percent of the total.
- Average length and standard deviation of missing data.

---
## __2.- Disclaimer__

The data which was used for this project were provided by the company in .json format. The data was anonymised by the company to comply with data protection on behalf of their clients, while still maintaining the integrity of the data to permit meaningful results from analysis.

---

## __3.- Libraries used__
Pandas, Seaborn, Matplotlib, Plotly, Prophet, Dash, Scikit-learn, Numpy, Configparser.

----


## __4.- Development steps__

### 4.1.  Exploratory data analysis. 
    
* [EDA1 - Data analysis](EDA/EDA1_data_analysis.ipynb)
* [EDA2 - Data visualisation ](EDA/EDA2_data_visualization.ipynb)


### 4.2. Machine Learning. Prophet Model.

After an initial study to determine which model would be best to achieve the desired outcomes, the company recommended [**Prophet**](https://facebook.github.io/prophet/docs/installation.html), an additive regression model developed by Meta (Facebook). 

Since each vehicle can have different temperature patterns, we included a number of hyperparameters filtered by vehicle and obtained the following files stored in  /prohpet_folder: 

| File | Default path* | Description |
| --- | --- | --- |
| **best_params_<vehicle_plate>.json** | dash_folder/best_parameters | Saves the best set of parameters which the model will use for each vehicle. |
| **perf_metrics_<vehicle_plate>.csv** | dash_folder/metrics | For each vehicle, selects the combination of hyperparameters with the best results.  |
| **modelo_<vehicle_plate>.json** | dash_folder/models | Houses the Prophet model that will be used for each vehicle to predict missing values. |
| **regrs_coef_<vehicle_plate>.txt** | dash_folder/regressors_coef | Identifies the regressors used and main statistics. |
| **figure_<vehicle_plate>.png** | dash_folder/saved_figures | Results with the figure and the statistical data after trainning the model with the best parameters. |


*Any folder path could be replaced in config.ini file.

When incorporating new data for any vehicle already analysed, the model will use the best parameters and regressors previously identified and saved.

### 4.3. Visualisation.

The Dash library was chosen for the visualisation of the data, since its core is based on Flask, React and Plotly for graphical visualisation in the web.
The result is an interactive web page permitting a visualisation of the data. 
![](/img/dashboard.gif)

---

## 5.- Installation

To obtain the full code, clone the following Git repository: 
```
$ git clone https://github.com/cmdl987/XXXX
```
All the necessary libraries and their dependencies are listed in the file requirements.txt. Instal the libraries via:
```
(venv) $ pip install -r requirements.txt 
```
The config file **config.ini** contains the information about the path were the different folders and parameters from prophet models are saved.

---


## 6.- Code implementation

To run the code, execute the file **main.py**.

```
(venv) $ python main.py
```
Warning! On running the code for the first time, the process may take some time to complete as no previously saved models exist and will have to be created. The time will depend on the machine running the code. On completing, a new window web page will open in your browser displaying the results.

---

---
# __Proyecto final: Predicción de datos faltantes y monitorización de temperatura [ES]__
El código de este repositorio fue realizado durante el mes de septiembre y octubre de 2022, dentro de las prácticas de empresa del _Curso de Programación en Python_ dentro de la Agencia para el Empleo del Ayuntamiento de Madrid y en colaboración con diferentes empresas pertenecientes al [**Clúster Big Data Madrid**](https://www.bigdatamadrid.org/). 

La planificación, desarrollo y ejecución del código fue llevada a cabo por: 

- Cristóbal Moreno (@cmdl987) [![GitHub](https://i.stack.imgur.com/tskMh.png) GitHub](https://github.com/cmdl987)     | [![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/cmorenodel/)
- Alex Fuller (@AlexFul) [![GitHub](https://i.stack.imgur.com/tskMh.png) GitHub](https://github.com/AlexFul)  |  [![Linkedin](https://i.stack.imgur.com/gVE0j.png) LinkedIn](https://www.linkedin.com/in/alex-fuller-7833031/)


-----

## __Índice:__
1. [Objetivos del proyecto](#1--objetivos-del-proyecto)
2. [Descargo de responsabilidad](#2--descargo-de-responsabilidad)
3. [Librerias empleadas](#3--librerias-empleadas)
4. [Pasos seguidos:](#4--pasos-seguidos)
    
    4.1. [Análisis de datos](#41-análisis-de-datos)

    4.2. [Machine Learning (Prophet)](#42-machine-learning-modelo-prophet)

    4.3. [Visualización](#43-visualización)

    
5. [Instalación](#5--instalación)
6. [Ejecución del código](#6--ejecución-del-código)

-----


## __1.- Objetivos del proyecto__


a) **Crear un modelo de rellenado de huecos con datos estimados en base a datos historicos**. Los datos provienen de la lectura y monitorizacion de sensores de temperatura durante el transporte de alimentos y medicamentos para realizar su trazabilidad.

b)  **Visualizar los resultados en un dashboard interactivo** con la librería Dash, siendo los KPIs principales:

- Gráficas que muestre la serie temporal de la temperatura real y los huecos rellenados en otro color, con registros de 5 minutos.
- Porcentaje de huecos faltantes sobre el total.
- Duración media y desviación típica de los huecos faltantes.

---
## __2.- Descargo de responsabilidad__

Los datos ofrecidos por la empresa y con los que se trabajaron durante el proyecto fueron cedidos bajo formato .json tras un proceso de anonimización de datos para garantizar la protección de datos por parte del cliente, a la vez que permitía mantener la veracidad de los resultados del tratamiento de los mismos. 

---

## __3.- Librerias empleadas__
Pandas, Seaborn, Matplotlib, Plotly, Prophet, Dash, Scikit-learn, Numpy, Configparser.

----


## __4.- Pasos seguidos__

### 4.1  Análisis exploratorio de datos (EDA). 
    

* [EDA1 - Análisis de datos ](EDA/EDA1_data_analysis.ipynb)
* [EDA2 - Visualización de datos ](EDA/EDA2_data_visualization.ipynb)


### 4.2. Machine Learning. Modelo Prophet.

Tras indagar en qué modelo sería el más adecuado para cumplir con los objetivos, la recomendación de la empresa fue [**Prophet**](https://facebook.github.io/prophet/docs/installation.html), un modelo de regresión aditivo desarrollado por Meta (Facebook). 

Como cada vehículo puede tener un comportamiento diferente ante los cambios de temperatura, se realiza un barrido de hiperparámetros a partir de nuestros datos filtrados por matrícula, con el cual se obtienen los siguientes archivos ubicados en el directorio /prophet_folder:

| Archivo | Path por defecto *| Descripción |
| --- | --- | --- |
| **best_params_<matrícula>.json** | dash_folder/best_parameters | Guarda los mejores parámetros que usará el modelo para determinada matrícula. |
| **perf_metrics_<matrícula>.csv** | dash_folder/metrics | Recoge los resultados de la combinación de cada hiperparámetro en la búsqueda del mejor modelo para cada matrícula. |
| **modelo_<matrícula>.json** | dash_folder/models | Constituye el modelo de Prophet que se cargará por cada matrícula para predecir los nuevos datos. |
| **regrs_coef_<matrícula>.txt** | dash_folder/regressors_coef | Identifica los regresores empleados y sus valores estadísticos. |
| **figure_<matrícula>.png** | dash_folder/saved_figures | Imagen con los resultados estadísticos del modelo entrenado con los mejores parámetros seleccionados. |


*Todas estas rutas relativas pueden ser reemplazadas cambiando los parámetros del archivo **config.ini**. 

Así, ante la entrada de nuevos datos para cada matrículas ya analizada, el modelo empleará los los mejores parámetros y regresores posibles guardados previamente.

### 4.3. Visualización.

Para la visualización de los datos se optó por la librería Dash, ya que su núcleo está constituido por Flask, React y Plotly para la visualización de las gráficas en el navegador.
El resultado es una página interactiva donde visualizar los datos. 
![](/img/dashboard.gif)

---

## 5.- Instalación

Para obtener el código completo, se ha de clonar el respositorio git: 
```
$ git clone https://github.com/cmdl987/XXXX
```
Todas las librerias y sus componentes necesarios están listados en el fichero requirements.txt. Instalar las librerías mediante:
```
(venv) $ pip install -r requirements.txt 
```
El archivo de configuración **config.ini** contiene las variables con las rutas de los diferentes directorios donde se guardan los archivos con los parámetros y los modelos extraídos de Prophet.

---

## 6.- Ejecución del código

Para hacer funcionar el código, se ejecutará el fichero **main.py**.

```
(venv) $ python main.py
```
¡Atención! Al no existir los modelos por primera vez el proceso puede demorarse unos minutos, debido al barrido de hiperparámetros para cada matrícula. Este tiempo dependerá del equipo. Posteriormente se abrirá una nueva ventana de su navegador con los resultados.

---

