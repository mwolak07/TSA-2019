from keras.optimizers import Adam
from keras.metrics import categorical_crossentropy
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.applications.mobilenet_v2 import MobileNetV2
from keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
import cv2
import matplotlib.pyplot as plt


def prepare_image(file):
    image_read = cv2.imread(file)
    image_resized = cv2.resize(image_read, (224, 224))
    image_array = np.array(image_resized)
    image_array_expanded = np.expand_dims(image_array, axis=0)
    return preprocess_input(image_array_expanded)


# Importing MobileNetV2 and discarding the last 1000 neuron layer
base_model = MobileNetV2(weights='imagenet', include_top=False)

# Adding dense layers to the model to learn more complex functions and better classify results
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
x = Dense(1024, activation='relu')(x)
x = Dense(512, activation='relu')(x)
final_layer = Dense(3, activation='softmax')(x)  # final layer with softmax activation

# Final model with new added architecture
model = Model(inputs=base_model.input, outputs=final_layer)

for i, layer in enumerate(model.layers):
    print(i, layer.name)

# Set first 20 layers to be non-trainable
for layer in model.layers[:20]:
    layer.trainable = False
for layer in model.layers[20:]:
    layer.trainable = True

# Pointing data generator to custom pre-processing function
datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

# Generating training data
train_generator = datagen.flow_from_directory('D:/TSA-2019-Dataset-Final/Training',
                                              target_size=(224, 224),
                                              color_mode='rgb',
                                              batch_size=32,
                                              class_mode='categorical',
                                              shuffle=True)

# Generating validation data
validation_generator = datagen.flow_from_directory('D:/TSA-2019-Dataset-Final/Validation',
                                                   target_size=(224, 224),
                                                   color_mode='rgb',
                                                   batch_size=32,
                                                   class_mode='categorical',
                                                   shuffle=True)

model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Setting the step size such that it fits the batch and dataset size
step_size_train = train_generator.n/train_generator.batch_size

step_size_validate = validation_generator.n/validation_generator.batch_size

# Fitting model on training, saving history data
history = model.fit_generator(generator=train_generator,
                              validation_data=validation_generator,
                              steps_per_epoch=step_size_train,
                              validation_steps=step_size_validate,
                              epochs=25)

# Save model
model.save('GunMLModel')

# Print accuracy graph
plt.plot(history.history['acc'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# Print loss graph
plt.plot(history.history['loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()
