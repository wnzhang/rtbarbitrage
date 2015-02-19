#!/usr/bin/python
import sys
import random
import math
import config

random.seed(10)

def bidding_const(bid):
    return bid

def bidding_rand(upper):
    return int(random.random() * upper)

def bidding_truth(r, pctr):
    return int(r * 1E3 * pctr)

def bidding_lin(pctr, base_ctr, base_bid):
    return int(pctr * base_bid / base_ctr)

def bidding_ortb(pctr, base_ctr, dsp_l, para):
    return int(math.sqrt(pctr * dsp_l * para / base_ctr + dsp_l * dsp_l) - dsp_l)

def bidding_sam_1(pctr, base_ctr, base_bid):
    return int(pctr * base_bid / base_ctr)

def bidding_sam_2(pctr, cam_r, dsp_l, one_over_dsp_lambda_plus_one):
    return int(math.sqrt(cam_r * 1E3 * dsp_l * pctr * one_over_dsp_lambda_plus_one + dsp_l * dsp_l) - dsp_l)

def bidding(original_ecpc, original_ctr, r, dsp_l, pctr, algo, para):
    bid = 0
    if algo == "const":
        bid = bidding_const(para)
    elif algo == "rand":
        bid = bidding_rand(para)
    elif algo == "truth":
        bid = bidding_truth(r, pctr)
    elif algo == "lin":
        bid = bidding_lin(pctr, original_ctr, para)
    elif algo == "ortb":
        bid = bidding_ortb(pctr, original_ctr, dsp_l, para)
    elif algo == "sam1" or algo == "sam1c":
        bid = bidding_sam_1(pctr, original_ctr, para)
    elif algo == "sam2" or algo == "sam2c":
        bid = bidding_sam_2(pctr, r, dsp_l, para)
    else:
        print 'wrong bidding strategy name (at arbitrage_rtb_test.py): ' + algo
        sys.exit(-1)
    return bid


def sample_cam(cam_vc):
    vsum = 0
    for cam in cam_vc:
        vsum += cam_vc[cam]
    s = random.random() * vsum
    sum = 0.
    for cam in cam_vc:
        sum += cam_vc[cam]
        if not sum < s:
            return cam
    # print "###"
    # print cam_vc
    # print s
    # print sum
    #return -1
    return cam_vc.keys()[random.randint(0, len(cam_vc)-1)]


def init_cam_data_index(cam_data):
    cam_data_index = {}
    for cam in cam_data:
        cam_data_index[cam] = 0
    return cam_data_index

def next_cam_data(cam_data, cam_data_index, cam_data_length, cam):
    data = -1
    if cam_data_index[cam] < cam_data_length[cam]:
        data = cam_data[cam][cam_data_index[cam]]
        cam_data_index[cam] += 1
    return data

def check_data_ran_out(cam_data_index, cam_data_length, cam_vc, volume):
    for cam in cam_data_index:
        if cam_data_index[cam] >= cam_data_length[cam]:
            cam_vc.pop(cam, None)
    sum = 0
    for cam in cam_data_index:
        sum += cam_data_index[cam]
    if sum >= volume:
        return True
    for cam in cam_data_index:
        if cam_data_index[cam] < cam_data_length[cam]:
            return False
    return True  # all the campaign data runs out, but less than the volume

def simulate_one_bidding_strategy_with_parameter(cam_data, cam_data_length, cam_r, cam_original_ecpc, cam_original_ctr,
                                                 dsp_budget, volume, dsp_l, cam_v, algo, para, tag, cm_up_value):
    # init
    cost = 0
    clks = 0
    bids = 0
    imps = 0
    profit = 0
    cam_data_index = init_cam_data_index(cam_data)
    budget_run_out = False
    cam_vc = cam_v.copy()
    data_run_out = check_data_ran_out(cam_data_index, cam_data_length, cam_vc, volume)

    # start simulation
    while (not data_run_out) and (not budget_run_out):
        cam = sample_cam(cam_vc)
        yzp = next_cam_data(cam_data, cam_data_index, cam_data_length, cam)
        original_ecpc = cam_original_ecpc[cam]
        original_ctr = cam_original_ctr[cam]
        clk = yzp[0]
        mp = yzp[1] + cm_up_value  # competition model
        pctr = yzp[2]
        r = cam_r[cam]
        bid = bidding(original_ecpc, original_ctr, r, dsp_l, pctr, algo, para)
        #bid = bidding(original_ecpc, original_ctr, r, config.cam_l[cam], pctr, algo, para)
        bids += 1
        if bid > mp:  # win auction
            imps += 1
            clks += clk
            cost += mp
            profit += clk * r - mp * 1.0E-3  # not cpm counting
        budget_run_out = (cost >= dsp_budget)
        data_run_out = check_data_ran_out(cam_data_index, cam_data_length, cam_vc, volume)

    alpha = "uniform"
    if config.alpha != "uniform":
        alpha = "%.5f" % config.alpha
    return "%s\t%s\t%s\t%.2f\t%d\t%d\t%d\t%d\t%d\t%.1f\t%s\t%.4f" % (tag, alpha, algo, profit, clks, bids, imps,
                                                     dsp_budget, cost, config.cpc_payoff_ratio, para, cm_up_value)

header = "prop\talpha\talgo\tprofit\tcvns\tbids\timps\tbudget\tcost\trratio\tpara\tup"