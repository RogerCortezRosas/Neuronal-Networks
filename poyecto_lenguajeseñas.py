# -*- coding: utf-8 -*-
"""poyecto_lenguajeSeñas.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hwTm7Y9mK34alJbikaL0u85QzqhVu7ve

# PROYECTO DE CURSO (Main Project)
## Descrición del lenguaje de señas MNIST (American Sign Language)
Este conjunto de datos se adoptó del lenguaje de señas MNIST, convirtiendo el archivo CSV en imágenes y también disminuyendo el tamaño general de la base de datos.

Hay un total de 27,455 imágenes en escala de grises de tamaño 28 * 28 píxeles cuyo valor oscila entre 0-255. Cada caso representa una etiqueta (0-25) como un mapa uno a uno para cada letra alfabética A-Z (y ningún caso para 9 = J o 25 = Z debido a movimientos gestuales).

Los datos se almacenan de forma ordenada y son compatibles para su uso con generadores de flujo de datos en la API de TensorFlow. Cada carpeta recibe un nombre de acuerdo con la clase de imágenes almacenadas en su interior, lo que facilita su carga y visualización.

Las imágenes se almacenan en formato de archivo 'JPEG'.

Los datos originales de la imagen del gesto de la mano representaban a varios usuarios que repitieron el gesto con diferentes fondos. Los datos del MNIST en lenguaje de señas provienen de una gran extensión del pequeño número (1704) de las imágenes en color incluidas como no recortadas alrededor de la región de interés de la mano.

Para crear nuevos datos, se usó una canalización de imágenes basada en ImageMagick e incluyó recortar a solo manos, escalar grises, cambiar el tamaño y luego crear al menos más de 50 variaciones para aumentar la cantidad. La estrategia de modificación y expansión fueron los filtros ('Mitchell', 'Robidoux', 'Catrom', 'Spline', 'Hermite'), junto con un 5% de pixelación aleatoria, +/- 15% de brillo / contraste y finalmente 3 grados de rotación. Debido al pequeño tamaño de las imágenes, estas modificaciones alteran efectivamente la resolución y la separación de clases de formas interesantes y controlables.

Fuente: TecPerson - Kaggle

## Obtencion de archivo de imagenes dede Google Cloud Platform
"""

!wget --no-check-certificate https://storage.googleapis.com/platzi-tf2/sign-language-img.zip \
    -O /tmp/sign-language-img.zip

"""## Descomprimir el archivo

En el siguiente código de Python utilizamos la libreria OS para poder dar acceso a los archivos del sistema operativo y luego con la librería ZipFile descomprimimos la base de datos
"""

import os
import zipfile

local_zip = '/tmp/sign-language-img.zip' # ruta que pusiste en el wget
zip_ref = zipfile.ZipFile(local_zip, 'r') # se cra objeto zip_ref para leer el archivo
zip_ref.extractall('/tmp') # extrae los archivos en el directorio /tmp
zip_ref.close() # IMPORTANTE CERRAR LA SESION

"""## Importamos librerias"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
# %matplotlib inline
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import string
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""## obtenemos la direcion de nuestras carpetas extraidas"""

train_dir = "/tmp/Train"
test_dir = "/tmp/Test"

"""## Data Generators
Configuremos generadores de datos que leerán imágenes en nuestras carpetas de origen, las convertirán en tensores `float32` y las alimentarán (con sus etiquetas) a nuestra red. Tendremos un generador para las imágenes de entrenamiento y otro para las imágenes de validación. Nuestros generadores producirán lotes de imágenes de tamaño 28x28 y sus etiquetas (clases lenguaje de señas).
"""

# Normalizacion de los datos para que los pixeles esten de 0-1
train_datagen = ImageDataGenerator(rescale = 1/255)
test_datagen = ImageDataGenerator(rescale = 1/255, validation_split= 0.2) # validation_split reserva 20% de los datos para validacion

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size = (28, 28), # estandarizar (cambia)el tamano de las matrices para evitar errores de tamanos
    batch_size = 128, # Cantidad de imagenes juntas que van entrenarse
    class_mode = "categorical",
    color_mode = "grayscale", # Indica el color de las imagenes
    subset = "training" # define a que corresponde es subset
)

validation_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size = (28, 28),
    batch_size = 128,
    class_mode = "categorical",
    color_mode = "grayscale",
    subset = "validation"
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size = (28, 28),
    batch_size = 128,
    class_mode = "categorical",
    color_mode = "grayscale"
)

"""# Creacion del modelo"""

import tensorflow as tf
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense,Input,ReLU,BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from  tensorflow.keras import models, optimizers, regularizers

def model1():

  model = models.Sequential([
      Input(shape=(28,28,1)),

      Conv2D(32,(2,2),padding="same"),
      BatchNormalization(),
      ReLU(),
      MaxPooling2D((2,2)),

      Conv2D(64,(2,2),padding="same"),
      BatchNormalization(),
      ReLU(),
      MaxPooling2D((2,2)),

      Conv2D(128,(2,2),padding="same"),
      BatchNormalization(),
      ReLU(),
      MaxPooling2D((2,2)),

      Flatten(),

      Dense(128,activation='relu'),
      Dropout(0.5),
      Dense(24,activation='softmax')
  ])


  return model

"""## Callback"""

checkpoint = ModelCheckpoint('best_wights.keras',monitor='val_accuracy', verbose= 1, save_best_only=True)

"""## Compilacion"""

model_1 = model1()

model_1.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])

"""## Entrenamiento"""

hist = model_1.fit(train_generator,
                  steps_per_epoch=len(train_generator),
                  epochs=50,
                  validation_data=validation_generator,
                  validation_steps=len(validation_generator),
                  callbacks=[checkpoint])

def visualitation(history):

  fig , ax = plt.subplots(1,2,figsize=(15,5))

  ax[0].plot(history.history['accuracy'],"go-",label='Entrenamiento accuracy')
  ax[0].plot(history.history['val_accuracy'],"ro-",label='Validacion accuracy')
  ax[0].set_title('Entrenamiento & validacion accuracy')
  ax[0].legend()
  ax[0].set_xlabel('Epochs')
  ax[0].set_ylabel('Accuracy')

  ax[1].plot(history.history['loss'],"go-",label='Entrenamiento loss')
  ax[1].plot(history.history['val_loss'],"ro-",label='Validacion loss')
  ax[1].set_title('Entrenamiento & validacion loss')
  ax[1].legend()
  ax[1].set_xlabel('Epochs')
  ax[1].set_ylabel('Loss')
  plt.show()

visualitation(hist)

"""# Ahora copiamos el modelo y le pasamos los mejores pesos que se registraron para evaluar con la informacion de test"""

from keras.models import clone_model

model1_2 = clone_model(model_1)

model1_2.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])

model1_2.load_weights('best_wights.keras')

model1_2.evaluate(test_generator)

"""# Keras Tuner

Nos permite automatizar el proceso de configuracion de las redes neuronales
"""

!pip install -q -U keras-tuner

import keras_tuner as kt
from tensorflow import keras

classes = [char for char in string.ascii_uppercase if char != "J" if char != "Z"]

def constructor_modelos(hp):
  # El objeto hp (generalmente una instancia de HyperParameters) permite definir y seleccionar diferentes valores de hiperparámetros durante el proceso de optimización.hp es un objeto de Keras Tuner que maneja los hiperparámetros.
  model = tf.keras.models.Sequential()
  model.add(tf.keras.layers.Conv2D(75, (3,3), activation= "relu", input_shape = (28, 28, 1)))
  model.add(tf.keras.layers.MaxPool2D((2,2)))
  model.add(tf.keras.layers.Flatten())

  hp_units = hp.Int("units", min_value = 32, max_value = 512, step = 32)
  model.add(tf.keras.layers.Dense(units=hp_units,activation = "relu", kernel_regularizer= regularizers.l2(1e-5)))
  model.add(tf.keras.layers.Dropout(0.2))
  model.add(tf.keras.layers.Dense(128,activation = "relu", kernel_regularizer= regularizers.l2(1e-5)))
  model.add(tf.keras.layers.Dropout(0.2))
  model.add(tf.keras.layers.Dense(len(classes), activation = "softmax"))

  hp_learning_rate = hp.Choice('learning_rate', values = [1e-2, 1e-3, 1e-4])

  model.compile(optimizer = keras.optimizers.Adam(learning_rate=hp_learning_rate),loss = "categorical_crossentropy", metrics = ["accuracy"])

  return model

tuner = kt.Hyperband(
    #kt.Hyperband es un algoritmo de optimización de hiperparámetros que encuentra la mejor configuración para un modelo de Machine Learning de manera eficiente.
    #Se basa en el algoritmo Hyperband, que optimiza el proceso de búsqueda de hiperparámetros al asignar más recursos a las configuraciones prometedoras y eliminar rápidamente las peores
    constructor_modelos,
    objective = "val_accuracy",
    max_epochs = 20,
    factor = 3, # Indica cuantos modelos pasaran a al siguiente ronda y el numero de epocas que aumentaran para medir a los que se quedaron
    directory = "models/",
    project_name = "platzi-tunner"
)

tuner.search(train_generator, epochs =20, validation_data = validation_generator) # Busqueda del mejor modelo

best_hps = tuner.get_best_hyperparameters(num_trials =1)[0]

print("Numero de neiuroanas conmejro calificacion",best_hps.get('units'))

"""### Creacion del hypermodelo"""

hypermodel = tuner.hypermodel.build(best_hps)

history_hypermodel = hypermodel.fit(
    train_generator,
    epochs = 20,
    callbacks = [callback_early],
    validation_data = validation_generator
)