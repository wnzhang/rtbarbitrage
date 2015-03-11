#!/usr/bin/python
import sys
import os
import random
import math
import config
import e_step_cam_selection
import m_step_bid_optimisation
import arbitrage_rtb_test
import portfolio_optimisation
import competitor_model
import bid_landscape_lazy

# setting: best train to test


if len(sys.argv) > 1:
    cams_str = sys.argv[1]
    cams = cams_str.strip().split()
    config.campaigns = cams
    if len(sys.argv) > 2:
        config.cpc_payoff_ratio = float(sys.argv[2])

random.seed(10)
config.alphas = [0.1, 2]
config.budget_proportions = [16]
config.data_folder = "../data/"

print "multiple campaign arbitrage driver"
print "test campaign: " + str(config.campaigns)
print "test algorithms:" + str(config.bid_algorithms)
print "payoff ratio:" + str(config.cpc_payoff_ratio)

cam_r = {}  # cam: payoff_cpc
cam_v = {}  # cam: selection_probability
cam_train_data = {}  # cam: [(yzp)]
cam_test_data  = {}  # cam: [(yzp)]
cam_train_data_length = {}
cam_test_data_length = {}
cam_original_ecpc = {}
cam_base_ctr = {}

dsp_clk = 0
dsp_cst = 0
dsp_imp = 0
dsp_bid = 0
dsp_lambda = 0

# start

# initialise
for cam in config.campaigns:
    cam_v[cam] = 1. / len(config.campaigns)
default_cam_v = cam_v.copy()

# read in train data
print "read in train data..."
for cam in config.campaigns:
    cam_train_data[cam] = []
    pctr_sum = 0.
    cost_sum = 0.
    clk_sum = 0.
    fi = open(config.data_folder + cam + ".train.txt", "r")
    for line in fi:
        s = line.strip().split("\t")
        clk = int(s[0])
        mp = int(s[1])
        pctr = float(s[2])
        clk_sum += clk
        cost_sum += mp
        pctr_sum += pctr
        cam_train_data[cam].append((clk, mp, pctr))
    fi.close()
    cam_train_data[cam].reverse()  # use the latest data for training
    cam_train_data_length[cam] = len(cam_train_data[cam])
    cam_original_ecpc[cam] = cost_sum * 1E-3 / clk_sum
    cam_r[cam] = cam_original_ecpc[cam] * config.cpc_payoff_ratio  # the profit setting for each campaign
    cam_base_ctr[cam] = pctr_sum / cam_train_data_length[cam]
    config.dsp_l = bid_landscape_lazy.get_optimal_l(cam_train_data)
    #dsp_original_cost += cost_sum


# read in test data
print "read in test data..."
dsp_original_cost_test = 0.
min_test_length = 1E9
for cam in config.campaigns:
    cam_test_data[cam] = []
    fi = open(config.data_folder + cam + ".test.txt", "r")
    for line in fi:
        s = line.strip().split("\t")
        cam_test_data[cam].append((int(s[0]), int(s[1]), float(s[2])))
        dsp_original_cost_test += int(s[1])
    fi.close()
    cam_test_data_length[cam] = len(cam_test_data[cam])
    if min_test_length > cam_test_data_length[cam]:
        min_test_length = cam_test_data_length[cam]
dsp_original_cost_test /= len(config.campaigns)  # average cost
config.volume = min_test_length
print "average campaign original cost test: " + str(dsp_original_cost_test)
print "test volume: " + str(config.volume)

# rock!
camstr = config.campaigns[0]
for i in range(1, len(config.campaigns)):
    camstr = camstr + "-" + config.campaigns[i]
config.result_file = config.data_folder + "multiple.campaign.arbitrage.demo.result.txt"
config.portfolio_file = config.data_folder + "multiple.campaign.arbitrage.demo.portfolio.txt"


fo = open(config.result_file, "w")
fpo = open(config.portfolio_file, "w")
header = arbitrage_rtb_test.header
print header
fo.write(header + "\n")

for alpha in config.alphas:
    config.alpha = alpha
    for proportion in config.budget_proportions:
        dsp_budget = dsp_original_cost_test / proportion

        for algo in config.bid_algorithms:
            # train
            em_rounds = config.em_rounds
            if alpha == "uniform":
                em_rounds = 1
            for round in range(em_rounds):
                # e-step
                if round == 0:
                    cam_v = default_cam_v.copy()
                else:
                    cam_v = e_step_cam_selection.e_step(cam_train_data, cam_train_data_length, cam_r, cam_base_ctr, dsp_budget,
                                      config.volume, config.dsp_l, cam_v, config.algo_one_para, algo, config.alpha)
                #print "e-step cam_v = " + str(cam_v)

                # m-step
                config.algo_one_para[algo] = m_step_bid_optimisation.m_step(cam_train_data, cam_train_data_length, cam_r, cam_base_ctr,
                                    dsp_budget, config.volume, config.dsp_l, cam_v, config.algo_paras, algo)
                #print "m-step algo_one_para = " + str(config.algo_one_para)

            fpo.write(str(proportion) + "\t" + str(config.alpha) + "\t" + algo + "\n")
            config.write_cached_Sigma_mu(fpo)
            fpo.write("\n")
            fpo.flush()
            #config.print_cached_Sigma_mu()

            # test
            #print "\ntest\n"
            #print header
            perf = arbitrage_rtb_test.simulate_one_bidding_strategy_with_parameter(cam_test_data,
                cam_test_data_length, cam_r, cam_original_ecpc, cam_base_ctr, dsp_budget, config.volume,
                config.dsp_l, cam_v.copy(), algo, config.algo_one_para[algo],
                "%s" % proportion, 0)
            print perf
            fo.write(perf + "\n")
            fo.flush()

            # cm
            if algo == "sam1" or algo == "sam2":
                cm_up_value = competitor_model.get_market_price_up_value(cam_train_data, cam_r, cam_original_ecpc,
                                                                         cam_base_ctr, config.dsp_l, algo,
                                                                         config.algo_one_para[algo])
                algo_cm = algo + "c"
                perf = arbitrage_rtb_test.simulate_one_bidding_strategy_with_parameter(cam_test_data,
                    cam_test_data_length, cam_r, cam_original_ecpc, cam_base_ctr, dsp_budget, config.volume,
                    config.dsp_l, cam_v.copy(), algo_cm, config.algo_one_para[algo],
                    "%s" % proportion, cm_up_value)
                print perf
                fo.write(perf + "\n")
                fo.flush()
fo.close()
fpo.close()