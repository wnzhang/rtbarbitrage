__author__ = 'weinan'

import math
import config

def win_sam(bid, l):
    return bid * 1. / (bid + l)

def win_ortb3(bid, l):
    return 1. - math.exp(- bid / l)

def get_optimal_l(cam_train_data):
    bid_upper = 322 # 300
    bid_num = {}
    for bid in range(0, bid_upper + 1):
        bid_num[bid] = 0
    for cam in cam_train_data:
        for yzp in cam_train_data[cam]:
            z = yzp[1]
            bid_num[z] += 1

    sum = 0
    for bid in bid_num:
        sum += bid_num[bid]

    if sum == 0:
        return config.dsp_l

    bid_win = {}
    acc = 0.
    for bid in range(0, bid_upper + 1):
        acc += bid_num[bid]
        bid_win[bid] = acc / sum

    # model win = b / (b + l)
    ls = range(1, bid_upper)
    min_loss = 9E50
    optimal_l = -1
    for l in ls:
        loss = 0
        for bid in range(0, bid_upper + 1):
            y = bid_win[bid]
            yp = win_sam(bid, l)
            loss += (y - yp) * (y - yp)
        if loss < min_loss:
            min_loss = loss
            optimal_l = l
    return optimal_l
