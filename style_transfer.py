import tensorflow as tf
import numpy as np
import cv2
import base64

def load_img_from_bytes(image_bytes, max_dim=512):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = tf.convert_to_tensor(img, dtype=tf.float32)
    img = tf.image.resize(img, (max_dim, max_dim))
    img = img[tf.newaxis, :]
    return img

def tensor_to_base64(tensor):
    img = tensor.numpy()
    img = np.squeeze(img, axis=0)
    img = np.clip(img, 0, 255).astype("uint8")
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode(".jpg", img)
    return base64.b64encode(buffer).decode("utf-8")

def run_style_transfer(content_bytes, style_path, num_iterations=150):
    content_img = load_img_from_bytes(content_bytes)
    style_img = load_img_from_bytes(open(style_path, "rb").read())

    extractor = tf.keras.applications.vgg19.VGG19(include_top=False, weights='imagenet')
    extractor.trainable = False

    style_layers = [
        "block1_conv1", "block2_conv1",
        "block3_conv1", "block4_conv1",
        "block5_conv1"
    ]
    content_layers = ["block5_conv2"]

    outputs = [extractor.get_layer(name).output for name in (style_layers + content_layers)]
    model = tf.keras.Model([extractor.input], outputs)

    def gram_matrix(tensor):
        temp = tf.transpose(tensor, (2, 0, 1))
        features = tf.reshape(temp, (temp.shape[0], -1))
        gram = tf.matmul(features, features, transpose_b=True)
        return gram

    content_output = model(content_img)[len(style_layers):]

    opt = tf.keras.optimizers.Adam(learning_rate=0.02)
    generated_img = tf.Variable(content_img)

    for i in range(num_iterations):
        with tf.GradientTape() as tape:
            outputs = model(generated_img)
            style_outputs = outputs[:len(style_layers)]
            content_outputs_new = outputs[len(style_layers):]

            style_loss = tf.add_n([
                tf.reduce_mean((gram_matrix(style_outputs[j]) -
                                gram_matrix(model(style_img)[j])) ** 2)
                for j in range(len(style_layers))
            ])

            content_loss = tf.add_n([
                tf.reduce_mean((content_outputs_new[k] - content_output[k]) ** 2)
                for k in range(len(content_layers))
            ])

            total_loss = style_loss * 0.01 + content_loss * 1.0

        grad = tape.gradient(total_loss, generated_img)
        opt.apply_gradients([(grad, generated_img)])

    return tensor_to_base64(generated_img)
