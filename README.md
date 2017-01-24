TensorFlow implementation of the Tensor Train (TT) -Toolbox.

# TensorNet example
As an example lets create a neural network with a TT-matrix as a fully-connected layer:
```
def build_tt_model(x):
  # A 784 x 625 TT-matrix.
  tt_W_1 = t3f.get_tt_variable('tt_W_1', shape=((4, 7, 4, 7), (5, 5, 5, 5)))
  h_1 = tf.nn.relu(t3f.matmul(tt_W_1, x))
  W_2 = tf.get_variable('W_2', shape=[625, 10])
  y = tf.matmul(W_2, h_1)
  return y
```

If you want to start from already trained network and compress its fully-connected layer, you may load the network, find the closes approximation of the existing layer matrix in the TT-format, and then finetune the model
```
y = build_tt_model(x)
with tf.variable_scope("", reuse=True):
  tt_W_1 = t3f.get_tt_variable('tt_W_1')
W_2 = tf.get_variable('W_2', shape=[625, 10])
tt_init_op = t3f.initialize_from_tensor(tt_W, W)
loss = tf.nn.softmax_cross_entropy_with_logits(y, labels)
train_step = tf.train.Adam(0.01).minimize(loss)
restorer = tf.train.Saver(var_list=original_variables)
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    restorer.restore(sess, 'checkpoint/path')
    sess.run(tt_init_op)
    # Finally do the finetuning.
    ...
```


# Tests
```
nosetests  --logging-level=WARNING
```