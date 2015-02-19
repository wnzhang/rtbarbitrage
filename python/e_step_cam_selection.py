__author__ = 'weinan'

import math
import numpy
import config
import arbitrage_rtb_test
import portfolio_optimisation


def estimate_mu_sigma(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume, dsp_l, cam_v,
                      algo_one_para, algo):
    cam_mu = {}
    cam_sigma = {}  # standard deviation
    para = algo_one_para[algo]
    for cam in cam_data:
        data = cam_data[cam]
        length = cam_data_length[cam]
        profit_margins = []
        index = 0
        for process in range(config.e_step_mu_process_num):
            cost = 0
            profit = 0
            for i in range(min(volume, len(data))):
                yzp = data[index]
                index = (index + 1) % length  # rotation
                clk = yzp[0]
                mp = yzp[1]
                pctr = yzp[2]
                r = cam_r[cam]

                # bid = 0
                # if algo == "sam":
                #     bid = arbitrage_rtb_test.bidding_sam(pctr, r, dsp_l, para)
                # elif algo == "lin":
                #     bid = arbitrage_rtb_test.bidding_lin(pctr, cam_base_ctr[cam], para)
                # elif algo == "ortb":
                #     bid = arbitrage_rtb_test.bidding_ortb(pctr, cam_base_ctr[cam], r, dsp_l, para)
                # else:
                #     print "e-step portfolio algorithm name error"

                bid = arbitrage_rtb_test.bidding(r / config.cpc_payoff_ratio, cam_base_ctr[cam], r, dsp_l, pctr, algo, para)

                if bid > mp:  # win auction
                    cost += mp * 1.0E-3 # should have the same unit
                    profit += clk * r - mp * 1.0E-3  # not cpm counting
                if cost >= dsp_budget:
                    break
            profit_margin = profit / max(cost, 0.1) # avoid zero division
            profit_margins.append(profit_margin)
        cam_mu[cam] = numpy.mean(profit_margins)
        cam_sigma[cam] = numpy.std(profit_margins)
    return cam_mu, cam_sigma


def e_step(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume, dsp_l, cam_v, algo_one_para,
           algo, alpha):
    # cam_correlation
    cam_cor = {}
    for cam1 in cam_data:
        for cam2 in cam_data:
            if cam1 == cam2:
                cam_cor[(cam1, cam2)] = 1  # a trivial campaign correlation

    # cam_mu and cam_sigma
    # print "e-step cam_mu cam_sigma estimation"
    (cam_mu, cam_sigma) = estimate_mu_sigma(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume,
                                            dsp_l, cam_v, algo_one_para, algo)

    #print "cam\tmu\tsigma"
    #for cam in cam_mu:
    #    print "%s\t%f\t%f" % (cam, cam_mu[cam], cam_sigma[cam])

    # portfolio optimisation
    # print "e-step portfolio optimisation"
    cam_v = portfolio_optimisation.solve_portfolio_with_cam_correlation(cam_mu, cam_sigma, cam_cor, alpha)

    return cam_v

def e_step_naive(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume, dsp_l, cam_v,
                 algo_one_para, alpha):
    cam_v = {}
    n = len(cam_data)
    i = 1
    for cam in cam_data:
        if i == n:
            i -= 1
        cam_v[cam] = 1. / math.pow(2, i)
        i += 1
    return cam_v

def e_step_greedy(mu, idx_cam):
    if len(idx_cam) <= 1:
        return {config.campaigns[0]: 1}
    rate = 10E-5
    sum = 0.
    cam_v = {}
    selected_idx = set([])
    for i in range(len(idx_cam)):
        idx = -1
        for j in idx_cam:
            if j not in selected_idx and (idx == -1 or mu[j] > mu[idx]):
                idx = j
        selected_idx.add(idx)
        cam_v[idx_cam[idx]] = 1 - sum - rate
        sum += 1 - sum - rate
        rate = rate * rate
    for cam in cam_v:
        cam_v[cam] = cam_v[cam] / sum
    return cam_v

