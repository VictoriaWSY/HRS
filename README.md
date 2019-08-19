Hierarchical Random Switching
=============================
Hierarchical Random Switching (HRS) is a stochastic defense technique which
converts a deterministic base model structure to a stochastic model in
order to protect the model from adversarial threats such as adversarial
(mis-classification) attack and adversarial reprogramming. The
figure below illustrates the structure of a HRS model.

![](https://github.com/KieranXWang/HRS/raw/master/Figures/ijcai_hrs.png)

In the inference phase, the active channel that processes the input of
each block is randomly assigned and ever-switching, leading to drastic but
unpredictable changes to the active path (the chain of activate channels
which has the same architecture as the base model).

For more details, please refer to our paper at IJCAI 2019.

If you have any questions, feel free to contact Xiao Wang by email kxw@bu.edu.


## Dependencies
This code requires `python 3` and the following packages: `tensorflow`,
`keras`, `numpy`.

This code is tested with `tensorflow 1.14.0`, `keras 2.2.4` and `numpy 1.16.4`.


## Train HRS
`python train_hrs.py [options]`

Options:
* `-- model_indicator`: the indicator of the trained model, which indicates
the HRS structure and will be used as the locator for retrieving trained model
weights. Format: `test_model[10][10]` for a two-block, 10 by 10 HRS model.
Default: `test_hrs[10][10]`.
* `--split`: the indicator of channel structures in each block. Default: `default`.
* `--train_schedule`: number of epochs for training each block. Default: `40 40`.
* `--dataset`: CIFAR or MNIST. Default: `CIFAR`.

Outputs:
Trained weights of each channel will be saved in `./Model/`.

### Customize Model Structure and Block Splitting
This can be done by adding options in `block_split_config.py` with unique indicators. Note that `get_split` needs to
return a list of functions that return Keras `Sequential` models for each block.

## Compute Test Accuracy

## Defense against Adversarial Attack

## Defense against Adversarial Reprogramming

