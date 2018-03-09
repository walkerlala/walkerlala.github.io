#!/usr/bin/python3
#coding:utf-8

from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf

def weight_variable(shape):
  """generates a weight variable of a given shape."""
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  """generates a bias variable of a given shape."""
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def lenet5(image):
    # tf.reshape():
    #   If one component of shape is the special value -1, the size of that
    #   dimension is computed so that the total size remains constant. In
    #   particular, a shape of [-1] flattens into 1-D. At most one component of
    #   shape can be -1.
    #
    # C1
    x_image = tf.reshape(x, [-1, 28, 28, 1])
    # 5x5 kernel size, map 1 image to 6 images (which are feature maps)
    W_conv1 = weight_variable([5, 5, 1, 6])
    b_conv1 = bias_variable([6])
    h_conv1 = tf.nn.relu(
                tf.nn.conv2d(x_image, W_conv1, strides=[1, 1, 1, 1], padding='SAME') + b_conv1)

    # The resulting data set will be of shape [-1, 28, 28, 6], where -1 is a
    # number the same as the -1 above

    # average pooling, downsamples by 2X
    #
    # In general for images, your input is of shape [batch_size, 64, 64, 3] for an
    # RGB image of 64x64 pixels.
    # The kernel size ksize will typically be [1, 2, 2, 1] if you have a 2x2 window
    # over which you take the maximum. On the batch size dimension and the channels
    # dimension, ksize is 1 because we don't want to take the maximum over multiple
    # examples, or over multiples channels
    h_pool1 = tf.nn.avg_pool(h_conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # C3
    # 5x5 kernel size, map 6 feature maps to 16 feature maps
    W_conv2 = weight_variable([5, 5, 6, 16])
    b_conv2 = bias_variable([16])
    h_conv2 = tf.nn.relu(
                tf.nn.conv2d(h_pool1, W_conv2, strides=[1, 1, 1, 1], padding='SAME') + b_conv2)
    # average pooling
    h_pool2 = tf.nn.avg_pool(h_conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # After 2 round of downsampling, our 28x28 image is down-sampled to 7x7x16
    # feature maps. Now we map it to 84 features
    W_fc1 = weight_variable([7 * 7 * 16, 1024])
    b_fc1 = bias_variable([1024])
    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 16])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])
    y_conv = tf.matmul(h_fc1, W_fc2) + b_fc2

    return y_conv

print("Loading data...")
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
print("Finishing loading data")

# Create the model
x = tf.placeholder(tf.float32, [None, 784])
y_conv = lenet5(x)

# true lable
y_ = tf.placeholder(tf.float32, [None, 10])

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=y_,
                                                        logits=y_conv)
# mean across a batch
cross_entropy = tf.reduce_mean(cross_entropy)

train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
correct_prediction = tf.cast(correct_prediction, tf.float32)
accuracy = tf.reduce_mean(correct_prediction)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(20000):
        batch_xs, batch_ys = mnist.train.next_batch(50)
        train_step.run(feed_dict={x: batch_xs , y_: batch_ys})
        # eval accuracy every 100 steps
        if i % 100 == 0:
            train_accuracy = accuracy.eval(feed_dict={x: batch_xs, y_: batch_ys})
            print('step %d, training accuracy %g' % (i, train_accuracy))

    print('test accuracy %g' % accuracy.eval(feed_dict={
                x: mnist.test.images, y_: mnist.test.labels}))

