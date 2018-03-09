#!/usr/bin/python3
#coding:utf-8

"""
Canonical AlexNet implementation seems like this:
| Layer | Type            | Maps   | Size    | Kernel Size | Stride | Padding | Activation |
| ----- | --------------- | ------ | ------- | ----------- | ------ | ------- | ---------- |
| Out   | Fully Connected | -      | 1000    | -           | -      | -       | Softmax    |
| F9    | Fully Connected | -      | 4096    | -           | -      | -       | ReLU       |
| F8    | Fully Connected | -      | 4096    | -           | -      | -       | ReLU       |
| C7    | Convolution     | 256    | 13x13   | 3x3         | 1      | SAME    | ReLU       |
| C6    | Convolution     | 384    | 13x13   | 3x3         | 1      | SAME    | ReLU       |
| C5    | Convolution     | 384    | 13x13   | 3x3         | 1      | SAME    | ReLU       |
| S4    | MaxPooling      | 256    | 13x13   | 3x3         | 2      | VALID   | -          |
| C3    | Convolution     | 256    | 27x27   | 5x5         | 1      | SAME    | ReLU       |
| S2    | Max Pooling     | 96     | 27x27   | 3x3         | 2      | VALID   | -          |
| C1    | Convolution     | 96     | 55x55   | 11x11       | 4      | SAME    | ReLU       |
| In    | Input           | 3(RGB) | 224x224 | -           | -      | -       | -          |

Following is a simplified implementation of it (a few layers removed)

This file is self-contained: once it runs well, it runs everywhere, provided you
have downloaded and installed Tensorflow of course...  It will automatically
download the dataset (if not exist) and extract it under cd.  """

import os
import sys
import pdb
import tarfile
import tempfile
import urllib.request
import tensorflow as tf
from functools import reduce

DATA_URL = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
BATCH_SIZE = 50

_data = []
_labels = []
_test_data = []
_test_labels = []
_data_index = 0
_test_data_index = 0

def check_dataset(dir="./"):
    """
    Check whether the dataset exist and valid.
    We are using the python version. Please see the description at
        https://www.cs.toronto.edu/~kriz/cifar.html
    """
    if not os.path.exists(dir):
        return False
    filepath1 = os.path.join(dir, "cifar-10-batches-py/data_batch_1")
    filepath2 = os.path.join(dir, "cifar-10-batches-py/data_batch_2")
    filepath3 = os.path.join(dir, "cifar-10-batches-py/data_batch_3")
    filepath4 = os.path.join(dir, "cifar-10-batches-py/data_batch_4")
    filepath5 = os.path.join(dir, "cifar-10-batches-py/data_batch_5")
    filepath6 = os.path.join(dir, "cifar-10-batches-py/test_batch")
    if(os.path.exists(filepath1) and os.path.exists(filepath2)
            and os.path.exists(filepath3) and os.path.exists(filepath4)
            and os.path.exists(filepath5) and os.path.exists(filepath6)):
        return True
    return False

def download_dataset(dir="./"):
    """
    Download cifar10 dataset (python version) and put it under @dir
    """
    _dir = os.path.join(dir, "cifar10-10-batches-py")
    if os.path.exists(_dir) and not os.path.isdir(_dir):
        print("Path exists and it is not directory: %s" % _dir)
        prit("Exit!")
        exit(1)
    if not os.path.exists(dir):
        os.mkdir(dir)

    filename = DATA_URL.split("/")[-1]
    filepath = os.path.join("/tmp", filename)
    if not os.path.exists(filepath):
        # data = requests.get(DATA_URL)
        response = urllib.request.urlopen(DATA_URL)
        with open(filepath, "wb") as file:
            file.write(response.read())
    tarfile.open(filepath, "r:gz").extractall(dir)

def unpickle(file):
    """
    Unpickle data.

    The returned dict (of each of the batch files) contains a dictionary with
    the following elements:

        data -- a 10000x3072 numpy array of uint8s. Each row of the array stores
        a 32x32 colour image. The first 1024 entries contain the red channel
        values, the next 1024 the green, and the final 1024 the blue.  The image
        is stored in row-major order, so that the first 32 entries of the array
        are the red channel values of the first row of the image.

        labels -- a list of 10000 numbers in the range 0-9. The number at index
        i indicates the label of the ith image in the array data.
    """
    import pickle
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

def rearrange_data(line):
    """
    The first 1024 entries contain the red channel value, and the next 1024
    channel contain the green and the next the blue. We want to rearrange it
    such that the first three entries contains the red/green/blue channel value
    of the first pixel.
    """
    index = []
    for i in range(0, 1024):
        index.append(i)
        index.append(i+1024)
        index.append(i+2048)
    return line[index]

def load_files(dir="./"):
    """
    Load data into memory.
    Each image will be of shape [3072], i.e., flattened.
    """
    if not check_dataset():
        print("Downloading cifar10 dataset...")
        download_dataset()
    else:
        print("Dataset existed.")

    sys.stdout.write("Loading dataset into memory...")
    sys.stdout.flush()

    def _append_data(filepath, is_test=False):
        dict = unpickle(filepath)
        data = dict[b"data"]
        labels = dict[b"labels"]
        for line, label in zip(data, labels):
            if not is_test:
                _data.append(rearrange_data(line).tolist())
                _labels.append([1 if x == label else 0 for x in range(0, 10)])
            else:
                _test_data.append(rearrange_data(line).tolist())
                _test_labels.append([1 if x == label else 0 for x in range(0, 10)])

    _append_data(os.path.join(dir, "cifar-10-batches-py/data_batch_1"))
    _append_data(os.path.join(dir, "cifar-10-batches-py/data_batch_2"))
    _append_data(os.path.join(dir, "cifar-10-batches-py/data_batch_3"))
    _append_data(os.path.join(dir, "cifar-10-batches-py/data_batch_4"))
    _append_data(os.path.join(dir, "cifar-10-batches-py/data_batch_5"))
    _append_data(os.path.join(dir, "cifar-10-batches-py/test_batch"), is_test=True)
    print("END")

def next_batch(batch_size=BATCH_SIZE, is_test=False):
    """
    Return @batch_size images. The data will be of shape [@batch_size, 3027]
    """
    global _data
    global _labels
    global _test_data
    global _test_labels
    global _data_index
    global _test_data_index
    data = []
    labels = []
    data_source = []
    labels_source = []
    current_index = 0
    if not is_test:
        data_source = _data
        labels_source = _labels
        current_index = _data_index
        _data_index = (_data_index + batch_size) % len(_data)
    else:
        data_source = _test_data
        labels_source = _test_labels
        current_index = _test_data_index
        _test_data_index = (_test_data_index + batch_size) % len(_test_data)

    for i in range(0, BATCH_SIZE):
        index = current_index + i
        data.append(data_source[index % len(data_source)])
        labels.append(labels_source[index % len(labels_source)])

    return data, labels

def weight_variable(shape):
    """generates a weight variable of a given shape."""
    initial = tf.truncated_normal(shape, stddev=0.1)
    weight = tf.Variable(initial, name="weights")
    # add to a collection so that we can retrieve weights for regularization
    tf.add_to_collection("weight_collection", weight)
    return weight

def bias_variable(shape):
    """generates a bias variable of a given shape."""
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def variable_summaries(var):
  """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
  with tf.name_scope('summaries'):
    mean = tf.reduce_mean(var)
    tf.summary.scalar('mean', mean)
    with tf.name_scope('stddev'):
      stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
    tf.summary.scalar('stddev', stddev)
    tf.summary.scalar('max', tf.reduce_max(var))
    tf.summary.scalar('min', tf.reduce_min(var))
    tf.summary.histogram('histogram', var)

def fc_layer(input_tensor, input_dim, output_dim, layer_name, act=tf.nn.relu):
  """Reusable code for making a fully connected neural net layer.

  It does a matrix multiply, bias add, and then uses relu to nonlinearize.
  It also sets up name scoping so that the resultant graph is easy to read,
  and adds a number of summary ops.
  """
  # Adding a name scope ensures logical grouping of the layers in the graph.
  with tf.name_scope(layer_name):
    # This Variable will hold the state of the weights for the layer
    with tf.name_scope('weights'):
      weights = weight_variable([input_dim, output_dim])
      variable_summaries(weights)
    with tf.name_scope('biases'):
      biases = bias_variable([output_dim])
      variable_summaries(biases)
    with tf.name_scope('Wx_plus_b'):
      preactivate = tf.matmul(input_tensor, weights) + biases
      tf.summary.histogram('pre_activations', preactivate)
    activations = act(preactivate, name='activation')
    tf.summary.histogram('activations', activations)
    return activations

def conv_layer(input_tensor, input_dim, output_dim, layer_name,
                kernel_shape=[5,5], strides=[1,1,1,1], padding='SAME', act=tf.nn.relu):
    """ Reusable code for a convolutional neural network layer """
    with tf.name_scope(layer_name):
        with tf.name_scope("weights"):
            weights = weight_variable([kernel_shape[0], kernel_shape[1],
                                        input_dim, output_dim])
            variable_summaries(weights)
        with tf.name_scope("biases"):
            biases = bias_variable([output_dim])
            variable_summaries(biases)
        with tf.name_scope("conv_preactivate"):
            conv = tf.nn.conv2d(input_tensor, weights, strides=strides, padding=padding)
            preactivate = tf.nn.bias_add(conv, biases)
            tf.summary.histogram("preactivate", preactivate)
        activations = act(preactivate)
        tf.summary.histogram('activations', activations)
        return activations

def alexnet(image, batch_size=50):
    """ Canonical alexnet implementation. See the network detail above
    Arg:
        images: pixels value in an array (transformed to a tensor)

    Return:
        logits
    """
    x_image = tf.reshape(image, [-1, 32, 32, 3])

    # Randomly crop a [height, width] section of the image.
    # distorted_image = tf.random_crop(x_image, [height, width, 3])

    # Randomly flip the image horizontally.
    # distorted_image = tf.image.random_flip_left_right(x_image)
    distorted_image = tf.map_fn(lambda image: tf.image.random_flip_left_right(image), x_image)

    # Because these operations are not commutative, consider randomizing
    # the order their operation.
    # NOTE: since per_image_standardization zeros the mean and makes
    # the stddev unit, this likely has no effect see tensorflow#1458.
    distorted_image = tf.map_fn(lambda image: tf.image.random_brightness(image, max_delta=63), distorted_image)
    distorted_image = tf.map_fn(lambda image: tf.image.random_contrast(image, lower=0.2, upper=1.8), distorted_image)

    # Subtract off the mean and divide by the variance of the pixels.
    float_image = tf.map_fn(lambda image: tf.image.per_image_standardization(image), distorted_image)

    # conv1
    conv1 = conv_layer(float_image, 3, 64, "conv1")

    #poo1
    pool1 = tf.nn.max_pool(conv1, ksize=[1,3,3,1], strides=[1,2,2,1], padding='SAME')

    #norm1
    norm1 = tf.nn.lrn(pool1, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)

    #conv2
    W_conv2 = weight_variable([5,5,64,64])
    conv2 = conv_layer(norm1, 64, 64, "conv2")

    #norm2
    norm2 = tf.nn.lrn(conv2, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)

    #poo2
    pool2 = tf.nn.max_pool(norm2, ksize=[1,3,3,1], strides=[1,2,2,1], padding='SAME')

    #fc1, fully connected layer
    reshape = tf.reshape(pool2, [-1, 8 * 8 * 64])
    fc1 = fc_layer(reshape, 8*8*64, 1024, "fc1")

    #local4
    # weights = weight_variable([384, 192])
    # biases = bias_variable([192])
    # local4 = tf.nn.relu(tf.matmul(local3, weights) + biases)


    # linear layer(WX + b),
    logits = fc_layer(fc1, 1024, 10, "output_layer", act=tf.identity)

    return logits

def image_summary(batch_xs, batch_ys):
    """ associate input images with its labels """
    x_image = tf.reshape(batch_xs, [-1, 32, 32, 3])
    # view image in tensorboard
    tf.summary.image("CIFAR10-IMAGE", x_image, max_outputs=1000)
    # batch_ys = tf.Print(batch_ys, [batch_ys], "This is ys:", summarize=501)
    batch_ys = tf.identity(batch_ys)

    return batch_ys

if __name__ == '__main__':

    # build the model for both training and testing
    sys.stdout.write("Builing AlexNet for cifar10 dataset...")
    sys.stdout.flush()

    # dataset placeholder
    x = tf.placeholder(tf.float32, [None, 3072])
    y_ = tf.placeholder(tf.float32, [None, 10])

    y_conv = alexnet(x)

    # visualize image
    image_summary_op = image_summary(x, y_)

    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=y_,
                                                            logits=y_conv)

    # l2 regularization
    # weights = tf.get_collection("weight_collection")
    # regularizer = reduce(tf.add, map(tf.nn.l2_loss, weights))
    # cross_entropy = tf.reduce_mean(cross_entropy + 0.1 * regularizer)

    cross_entropy = tf.reduce_mean(cross_entropy)
    tf.summary.scalar('cross_entropy', cross_entropy)

    global_step = tf.Variable(0, trainable=False)
    starter_learning_rate = 0.01
    learning_rate = tf.train.exponential_decay(
            learning_rate = starter_learning_rate,
            global_step = global_step,
            decay_steps = 100000,
            decay_rate = 0.96,
            staircase=True
        )
    # train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    train_step = (
            tf.train.GradientDescentOptimizer(learning_rate)
            .minimize(cross_entropy, global_step=global_step)
        )

    # test
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    correct_prediction = tf.cast(correct_prediction, tf.float32)
    accuracy = tf.reduce_mean(correct_prediction)
    tf.summary.scalar('accuracy', accuracy)
    print("END")

    load_files()

    print("Training...")
    with tf.Session() as sess:

        # Merge all the summaries and write them out to /tmp/mnist_logs (by default)
        merged = tf.summary.merge_all()
        train_writer = tf.summary.FileWriter("/tmp/cifar10-summary" + '/train', sess.graph)
        test_writer = tf.summary.FileWriter("/tmp/cifar10-summary" + '/test')

        # NOTE: By default tf.global_variables_initializer() does not specify
        # variable initialization order. If an initialization of one variable
        # depends on another, you might get errors. In this case, it is better
        # to initialize one by one:
        #
        #   v = tf.get_variable("v", shape=(), initializer=tf.zeros_initializer())
        #   w = tf.get_variable("w", initializer=v.initialized_value() + 1)
        #
        initializer = tf.global_variables_initializer()
        sess.run(initializer)

        for i in range(20000):
            batch_xs, batch_ys = next_batch(50)
            summary_train, ts, _ = sess.run([merged, train_step, image_summary_op],
                                        feed_dict={x: batch_xs, y_: batch_ys})
            train_writer.add_summary(summary_train, i)

            # eval accuracy every 100 steps
            if i % 10 == 0:
                summary_accuracy, train_accuracy = sess.run([merged, accuracy],
                                                            feed_dict={x: batch_xs, y_: batch_ys})
                test_writer.add_summary(summary_accuracy, i)
                print('Step %d, training accuracy %g' % (i, train_accuracy))

        # test_xs, test_ys = next_batch(50, is_test=True)
        # print('test accuracy %g' % accuracy.eval(feed_dict={x: test_xs, y_: test_ys}))
        print('test accuracy %g' % accuracy.eval(feed_dict={x: _test_data, y_: _test_labels}))

