#!/usr/bin/python3
#coding:utf-8

# pylint: disable=superfluous-parens, invalid-name, broad-except, missing-docstring

import math

#initialize weight
w = 0.5
v = 0.5
b = 0.5
learning_rate = 0.5

"""
    x_t_sum = w * x_t + v * u_t + b
    y_t_sum = w * x_t + v * u_t + b
    x_t = sigmoid(x_t_sum),
    y_t = sigmoid(y_t_sum),
(we could change any sigmoid to tanh)
where:
w is the recurrent weight,
v is the input weight
b it the bais
"""

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def sum_recursive(seq, pred_seq, upperbound, r, previous_part):
    if r < 0:
        return 0
    if r == 0:
        x_t_own = 0
    else:
        x_t_own = pred_seq[r-1]
    in_t = seq[r]
    sg = sigmoid(w * x_t_own + v * in_t + b)
    own_part = sg * (1 - sg) * x_t_own

    if r == upperbound:
        left_part = 1
    else:
        left_own = pred_seq[r]
        left_in_t = seq[r+1]
        sg_left_own = sigmoid(w * left_own + v * left_in_t + b)
        left_part = sg_left_own * (1 - sg_left_own) * w
        left_part = previous_part * left_part

    return (left_part * own_part) + sum_recursive(seq, pred_seq, upperbound, r-1, left_part)

def calculate_w_grad(seq, pred_seq, i):
    # + 0.0001 so that it won't cause Divided-by-zero-Exception
    de_over_dxt = -seq[i] / (pred_seq[i] + 0.0001) + (1 - seq[i]) / (1 - pred_seq[i])
    g = sum_recursive(seq, pred_seq, i, i, 1)
    return de_over_dxt * g

def calculate_v_grad(seq, pred_seq, i):
    # + 0.0001 so that it won't cause Divided-by-zero-Exception
    de_over_dxt = -seq[i] / (pred_seq[i] + 0.0001) + (1 - seq[i]) / (1 - pred_seq[i])
    if i == 0:
        x_t_1 = 0
    else:
        x_t_1 = pred_seq[i-1]
    in_t = seq[i]
    sg = sigmoid(w * x_t_1 + v * in_t + b)
    derivative = sg * (1 - sg)
    return de_over_dxt * derivative * in_t

def calculate_b_grad(seq, pred_seq, i):
    # + 0.0001 so that it won't cause Divided-by-zero-Exception
    de_over_dxt = -seq[i] / (pred_seq[i] + 0.0001) + (1 - seq[i]) / (1 - pred_seq[i])
    if i == 0:
        x_t_1 = 0
    else:
        x_t_1 = pred_seq[i-1]
    in_t = seq[i]
    sg = sigmoid(w * x_t_1 + v * in_t + b)
    derivative = sg * (1 - sg)
    return de_over_dxt * derivative

def rnn(in_seq):
    global w
    global v
    global b

    # train RNN with 3000 round
    for _ in range(3000):
        x_t_1 = 0
        pred_seq = []
        for index, in_t in enumerate(in_seq):
            x_t = sigmoid(w * x_t_1 + v * in_t + b)
            pred_seq.append(x_t)

            w_gradient = 0
            v_gradient = 0
            b_gradient = 0

            for i in range(index + 1):
                w_gradient += calculate_w_grad(in_seq, pred_seq, i)
                v_gradient += calculate_v_grad(in_seq, pred_seq, i)
                b_gradient += calculate_b_grad(in_seq, pred_seq, i)

            w_gradient = w_gradient / (index + 1)
            v_gradient = v_gradient / (index + 1)
            b_gradient = b_gradient / (index + 1)

            w = w - learning_rate * w_gradient
            v = v - learning_rate * v_gradient
            b = b - learning_rate * b_gradient

            x_t_1 = x_t

    print("Finished training: w: %f, v: %f, b: %f" % (w, v, b))

    print("Start to predict:")
    x_t_1 = 0
    for in_t in in_seq:
        x_t = sigmoid(w * x_t_1 + v * in_t + b)
        print("Result %f\t%f" % (in_t, x_t))
        x_t_1 = x_t

rnn([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.1,0.3,0.5,0.7])
