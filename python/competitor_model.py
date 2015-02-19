__author__ = 'weinan'
import arbitrage_rtb_test

def get_market_price_up_value(cam_data, cam_r, cam_original_ecpc, cam_original_ctr,
                              dsp_l, algo, para):
    up_value = 0.
    num = 0
    for cam in cam_data:
        data = cam_data[cam]
        original_ecpc = cam_original_ecpc[cam]
        original_ctr = cam_original_ctr[cam]
        r = cam_r[cam]
        for yzp in data:
            clk = yzp[0]
            mp = yzp[1]
            pctr = yzp[2]
            bid = arbitrage_rtb_test.bidding(original_ecpc, original_ctr, r, dsp_l, pctr, algo, para)
            if bid > mp:
                up_value += (bid - mp) * 0.5
            num += 1
    up_value /= num
    return up_value