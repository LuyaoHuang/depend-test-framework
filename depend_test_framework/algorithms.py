import itertools
import tensorflow as tf
import numpy
import random
import os
from tensorflow.contrib import rnn

from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)


def route_permutations(graph, start, target,
                       trace=None, history=None, pb=None,
                       allow_dep=None, dep=None):
    routes = []
    nodes_map = graph[start]

    if not trace:
        new_trace = set([start])
    else:
        new_trace = set(trace)
        new_trace.add(start)

    if history is None:
        history = {}

    # TODO better way to limit the table
    if allow_dep:
        dep = dep or 0
        if dep >= allow_dep:
            return routes
        else:
            dep += 1

    for node, opaque in nodes_map.items():
        if node in new_trace:
            continue
        if node in history.keys():
            ret = history[node]
        else:
            if node == target:
                routes.append([opaque])
                continue
            else:
                ret = route_permutations(graph,
                    node, target, new_trace, history,
                    pb, allow_dep, dep)
        if ret:
            for sub_route in ret:
                tmp_route = [opaque]
                tmp_route.extend(sub_route)
                routes.append(tmp_route)

    del(new_trace)
    history[start] = routes
    if pb:
        pb.update(len(history) + 1)
    # LOGGER.info("Trace: %s", trace)
    # LOGGER.info("Map: %s", nodes_map)
    # LOGGER.info("Start: %s", start)
    # LOGGER.info("routes: %s", routes)
    return routes


class hashable_list(list):
    def __hash__(self):
        return hash(str(self))


class LSTM(object):
    def __init__(self, input_size, timesteps, output_size, num_hidden=128, learning_rate=0.001):
        def RNN(x, weights, biases):

            x = tf.unstack(x, timesteps, 1)

            # Define a lstm cell with tensorflow
            #lstm_cell = rnn.BasicLSTMCell(num_hidden, forget_bias=1.0)
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

    def _create_batch(self, datas, batch_size=100, mem_reply=True, random_batch=False):
        list_batch_x, list_batch_y = [], []
        memory = []
        y_size = 0
        for arr_x, arr_y in datas:
            list_batch_x.append(arr_x)
            list_batch_y.append(arr_y)
            y_size = arr_y.size
            if mem_reply:
                memory.append((arr_x, arr_y))
                if len(memory) < batch_size:
                    continue

                tmp = random.sample(memory, batch_size - 1)
                batch_x, batch_y = zip(*tmp)
                batch_x, batch_y = list(batch_x), list(batch_y)
                batch_x.append(arr_x)
                batch_y.append(arr_y)
                batch_x = numpy.array(batch_x)
                batch_y = numpy.array(batch_y)
                batch_y = numpy.reshape(batch_y, (batch_size, y_size))
                yield batch_x, batch_y
            elif len(list_batch_x) == batch_size:
                batch_x = numpy.array(list_batch_x)
                batch_y = numpy.array(list_batch_y)
                list_batch_x, list_batch_y = [], []
                batch_y = numpy.reshape(batch_y, (batch_size, y_size))
                yield batch_x, batch_y

        if random_batch:
            if not mem_reply:
                raise Exception

            while True:
                tmp = random.sample(memory, batch_size)
                batch_x, batch_y = zip(*tmp)
                batch_x, batch_y = list(batch_x), list(batch_y)
                batch_x = numpy.array(batch_x)
                batch_y = numpy.array(batch_y)
                batch_y = numpy.reshape(batch_y, (batch_size, y_size))
                yield batch_x, batch_y

    def _single_batch(self, datas):
        data_list = list(datas)
        arr_x, arr_y = list(self._create_batch(data_list,
                                               batch_size=len(data_list),
                                               mem_reply=False))[0]
        return arr_x, arr_y

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
        for batch_x, batch_y in self._create_batch(datas, random_batch=True):
            sess.run(self.train_op, feed_dict={self.X: batch_x, self.Y: batch_y})
            if debug:
                loss, acc = sess.run([self.loss_op, self.accuracy],
                                     feed_dict={self.X: batch_x, self.Y: batch_y})
                LOGGER.info("Step " + str(i) + ", Minibatch Loss= " + \
                            "{:.4f}".format(loss) + ", Training Accuracy= " + \
                            "{:.3f}".format(acc))
            i += 1
            if i > 1000:
                break

    def run(self, input_data):
        return self.sess.run(self.accuracy, feed_dict={self.X: input_data, self.Y: test_label})

    def test(self, datas):
        batch_x, batch_y = self._single_batch(datas)
        return self.sess.run(self.accuracy, feed_dict={self.X: batch_x, self.Y: batch_y})

    def save(self, path):
        self.saver.save(self.sess, path)

    def restore(self, path):
        self._init_sess(init=False)
        if os.path.exists(path + '.index'):
            self.saver.restore(self.sess, path)


def unit_test():
    G = {'s': {'u': 10, 'x': 5},
         'u': {'v': 1, 'x': 2},
         'v': {'y': 4},
         'x': {'u': 3, 'v': 9, 'y': 2},
         'y': {'s': 7, 'v': 6}}
    LOGGER.info(route_permutations(G, 's', 'u'))
    LOGGER.info(route_permutations(G, 'x', 'y'))

if __name__ == '__main__':
    unit_test()
