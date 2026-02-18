
# train_model.py
# Simple transfer learning training script (MobileNetV2)
# Prepare dataset/ modern, minimalist, industrial folders before running.

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import tensorflow as tf

datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    validation_split=0.2,
    rotation_range=15,
    horizontal_flip=True,
    zoom_range=0.15,
)

train_data = datagen.flow_from_directory(
    "dataset/",
    target_size=(244, 244),
    batch_size=16,
    subset="training"
)
val_data = datagen.flow_from_directory(
    "dataset/",
    target_size=(244, 244),
    batch_size=16,
    subset="validation"
)

base = MobileNetV2(weights="imagenet", include_top=False, input_shape=(244,244,3))

base.trainable = False
model = models.Sequential([
    base,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation="relu"),
    layers.Dense(train_data.num_classes, activation="softmax")
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
history = model.fit(train_data, validation_data=val_data, epochs=8)
model.save("backend/room_style_model.h5")
print("Saved model to backend/room_style_model.h5")



