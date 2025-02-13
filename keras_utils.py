import keras
import os
import tensorflow as tf

from keras.models import Model, Sequential
from keras.layers import InputLayer
from keras.engine.topology import Layer

from project_utils import get_dimensions


class RandomMask(Layer):
    def __init__(self, nb_channels, **kwargs):
        self.nb_channels = nb_channels
        self.mask = None
        super().__init__(**kwargs)

    def build(self, input_shape):
        # the input_shape here should be a list
        assert isinstance(input_shape, list), "the input shape of RandomMask layer should be a list"
        shape = input_shape[0]

        # build the random mask
        if self.nb_channels == 1:
            self.mask = tf.ones((1, ) + shape[1:])
        else:
            ones = tf.ones((1, ) + shape[1:])
            zeros = tf.zeros((self.nb_channels - 1, ) + shape[1:])
            mask = tf.concat([ones, zeros], 0)
            self.mask = tf.random_shuffle(mask)
            pass

    def call(self, x):
        # x should be a list
        assert isinstance(x, list), "the input of RandomMask layer should be a list"
        xs_expand = [tf.expand_dims(x_orig, axis=1) for x_orig in x]
        x = tf.concat(xs_expand, 1)
        x = x * self.mask
        x = tf.reduce_sum(x, axis=1)
        return x

    def compute_output_shape(self, input_shape):
        shape = input_shape[0]
        return shape


def construct_model_by_blocks(block_list):
    # connect all blocks
    if len(block_list) == 1:
        i = block_list[0].input
        o = block_list[0].output
    else:
        i = block_list[0].input
        o = block_list[0].output
        idx = 1
        while idx < len(block_list):
            o = block_list[idx](o)
            idx += 1
    model = Model(input=i, output=o)

    return model


# def construct_switching_blocks(dataset, indicator, structure, blocks_definition, load_weights=True):
#     '''
#     Note: structure can be different from indicator, indicator will only be used to load weights (if load_weights ==
#     True). This is so designed because this function may be used to construct the switching part of HRS model under
#     training.
#     '''
#
#     # assert nb blocks
#     assert len(structure) == len(blocks_definition), 'arg structure and block_definition need to have the same length'
#     nb_block = len(structure)
#
#     # assert weights exist
#     weights_dir = './Model/%s_Models/%s' % (dataset, indicator)
#     assert os.path.exists(weights_dir), '%s does not exist' % weights_dir
#
#     # input
#     img_rows, img_cols, img_channels = get_dimensions(dataset)
#     model_input = InputLayer(input_shape=(img_rows, img_cols, img_channels))
#
#     # loop over blocks
#     block_input = model_input
#     for i in range(nb_block):
#         for j in range(structure[i]):
#             channel = blocks_definition[i]()


def construct_switching_block(input, nb_channels, channel_definition, weights, freeze_channel=True):

    channel_output_list = []
    for channel_idx in range(nb_channels):
        channel = channel_definition()
        channel_output = channel(input)
        channel_output_list.append(channel_output)
        # load weights
        if weights:
            channel.load_weights(weights % channel_idx)
        if freeze_channel:
            for layer in channel.layers:
                layer.trainable = False

    # using a random mask to mask inactive channels
    block_output = RandomMask(nb_channels)(channel_output_list)
    return block_output


def construct_hrs_model(dataset, model_indicator, blocks_definition, load_weights=True):
    # get structure from model_indicator
    structure = [int(ss[:-1]) for ss in model_indicator.split('[')[1:]]
    nb_block = len(structure)

    # assert nb blocks
    assert len(structure) == len(blocks_definition), 'arg structure and block_definition need to have the same length'

    # assert weights exist
    weights_dir = './Model/%s_Models/%s' % (dataset, model_indicator)
    assert os.path.exists(weights_dir), '%s does not exist' % weights_dir

    # input
    img_rows, img_cols, img_channels = get_dimensions(dataset)
    model_input = InputLayer(input_shape=(img_rows, img_cols, img_channels))
    save_dir = './Model/%s_models/' % dataset + model_indicator + '/'

    # loop over block
    block_input = model_input.output
    for i in range(nb_block):
        weight_dir = save_dir + '%d_' % i + '%d'
        block_output = construct_switching_block(input=block_input, nb_channels=structure[i],
                                                 channel_definition=blocks_definition[i], weights=weight_dir)
        block_input = block_output

    # construct Model object
    model = Model(input=model_input.input, output=block_output)

    return model

