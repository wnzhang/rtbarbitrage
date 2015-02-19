__author__ = 'weinan'

import math
import arbitrage_rtb_test
import config


def check_lambda(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume, dsp_l, cam_v, dsp_lambda_plus_one):
    cost = 0
    for cam in cam_data:
        cam_cost = 0
        for yzp in cam_data[cam]:
            #clk = yzp[0]
            #mp = yzp[1]
            pctr = yzp[2]
            bid = arbitrage_rtb_test.bidding_sam(pctr, cam_r[cam], dsp_l, dsp_lambda_plus_one)
            win_prob = bid * 1.0 / (bid + dsp_l)
            cam_cost += bid * win_prob
        cam_cost /= len(cam_data[cam])
        cost += cam_v[cam] * cam_cost
    loss = math.fabs(dsp_budget / volume - cost) / (dsp_budget / volume)
    print "dsp_budget\t%d\tvolume\t%d\td/v\t%.4f\tcost\t%.4f" % (dsp_budget, volume, dsp_budget / volume, cost)
    return loss

def check_lambda_by_profit(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume, dsp_l, cam_v, para, algo):
    # init
    cost = 0
    profit = 0
    budget_run_out = False
    cam_data_index = arbitrage_rtb_test.init_cam_data_index(cam_data)
    cam_vc = cam_v.copy()  # we will change cam_vc when one campaign runs out of data
    data_run_out = arbitrage_rtb_test.check_data_ran_out(cam_data_index, cam_data_length, cam_vc, volume)

    # start simulation
    while (not data_run_out) and (not budget_run_out):
        cam = arbitrage_rtb_test.sample_cam(cam_vc)
        yzp = arbitrage_rtb_test.next_cam_data(cam_data, cam_data_index, cam_data_length, cam)
        if yzp == -1:
            print cam_data_length
            print cam_data_index
        clk = yzp[0]
        mp = yzp[1]
        pctr = yzp[2]
        r = cam_r[cam]
        bid = arbitrage_rtb_test.bidding(r / config.cpc_payoff_ratio, cam_base_ctr[cam], r, dsp_l, pctr, algo, para)
        if bid > mp:  # win auction
            cost += mp
            if algo == "lin" or algo == "ortb":
                profit += clk  # these two algorithms care about clicks
            else:
                profit += clk * r - mp * 1.0E-3  # not cpm counting

        budget_run_out = (cost >= dsp_budget)
        data_run_out = arbitrage_rtb_test.check_data_ran_out(cam_data_index, cam_data_length, cam_vc, volume)
    return -profit

def m_step(cam_data, cam_data_length, cam_r, cam_base_ctr, dsp_budget, volume, dsp_l, cam_v, algo_paras, algo):
    optimal_para = -1
    min_loss = 9E100
    paras = algo_paras[algo]
    for para in paras:
        loss = check_lambda_by_profit(cam_data, cam_data_length, cam_r, cam_base_ctr,
                                      dsp_budget, volume, dsp_l, cam_v, para, algo)
        #print str(cam_v) + "\t" + algo + " para\t" + str(para) + "\tloss\t" + str(loss)
        if loss < min_loss:
            min_loss = loss
            optimal_para = para
    #print str(cam_v) + "\t" + algo + " optimal para: " + str(optimal_para) + "\tloss: " + str(min_loss)
    return optimal_para