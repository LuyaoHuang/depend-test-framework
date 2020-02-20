"""
Deep learning algorithms
"""
import tensorflow as tf
import numpy
import random
import os
from tensorflow.contrib import rnn

from depend_test_framework.log import get_logger

LOGGER = get_logger(__name__)


class LSTM(object):
    def __init__(self, input_size, timesteps, output_size, num_hidden=128, learning_rate=0.001):
        def RNN(x, weights, biases):

            x = tf.unstack(x, timesteps, 1)

            # Define a lstm cell with tensorflow
            # lstm_cell = rnn.BasicLSTMCell(num_hidden, forget_bias=1.0)
            lstm_cell = rnn.BasicLSTMCell(num_hidden)

            # Get lstm cell output
            outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)

            # Linear activation, using rnn inner loop last output
            return tf.matmul(outputs[-1], weights['out']) + biases['out']

        self.X = X = tf.placeholder("float", [None, timesteps, input_size])
        self.Y = Y = tf.placeholder("float", [None, output_size])
        weights = {
            'out': tf.Variable(tf.random_normal([num_hidden, output_size]))
        }
        biases = {
            'out': tf.Variable(tf.random_normal([output_size]))
        }

        logits = RNN(X, weights, biases)
        prediction = tf.nn.softmax(logits)
        self.loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
            logits=logits, labels=Y))
        optimizer = tf.train.RMSPropOptimizer(learning_rate=learning_rate)
        self.train_op = optimizer.minimize(self.loss_op)

        # Evaluate model (with test logits, for dropout to be disabled)
        correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(Y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

        # Initialize the variables (i.e. assign their default value)
        self.init = tf.global_variables_initializer()
        self.saver = tf.train.Saver()
        self.sess = None

    def _transfer_dataset(self, datas, batch_size=100, random=False, repeat=False, parser=None):
        list_x, list_y = zip(*datas)
        arr_x, arr_y = numpy.array(list_x), numpy.array(list_y)
        # FIXME
        arr_y = arr_y.reshape((arr_y.shape[0], arr_y.shape[-1]))
        data_set = tf.contrib.data.Dataset.from_tensor_slices((arr_x, arr_y))
        if parser:
            data_set = data_set.map(parser)
        if random:
            data_set = data_set.shuffle(buffer_size=1000)
        data_set = data_set.batch(batch_size)
        if repeat:
            data_set = data_set.repeat()
        return data_set.make_initializable_iterator()

    def _init_sess(self, init=True):
        if not self.sess:
            self.sess = tf.Session()
            if init:
                self.sess.run(self.init)
        return self.sess

    def train(self, datas, debug=False):
        sess = self._init_sess()
        i = 0
        LOGGER.info('Start training ...')
        iterator = self._transfer_dataset(datas, random=True, repeat=True)
        next_element = iterator.get_next()
        sess.run(iterator.initializer)
        # writer = tf.summary.FileWriter("/tmp/log/test", sess.graph)

        while True:
            batch_x, batch_y = sess.run(next_element)
            sess.run(self.train_op, feed_dict={self.X: batch_x, self.Y: batch_y})
            if debug:
                loss, acc = sess.run([self.loss_op, self.accuracy],
                                     feed_dict={self.X: batch_x, self.Y: batch_y})
                LOGGER.info("Step " + str(i) + ", Minibatch Loss= " +
                            "{:.4f}".format(loss) + ", Training Accuracy= " +
                            "{:.3f}".format(acc))
            i += 1
            if i > 1000:
                break
        # writer.close()

    def run(self, input_data):
        # return self.sess.run(self.accuracy, feed_dict={self.X: input_data, self.Y: test_label})
        return

    def test(self, datas):
        self._init_sess()
        list_x, list_y = zip(*datas)
        arr_x, arr_y = numpy.array(list_x), numpy.array(list_y)
        arr_y = arr_y.reshape((arr_y.shape[0], arr_y.shape[-1]))
        return self.sess.run(self.accuracy, feed_dict={self.X: arr_x, self.Y: arr_y})

    def save(self, path):
        self.saver.save(self.sess, path)

    def restore(self, path):
        self._init_sess(init=False)
        if os.path.exists(path + '.index'):
            self.saver.restore(self.sess, path)

    def __del__(self):
        if self.sess:
            self.sess.close()
