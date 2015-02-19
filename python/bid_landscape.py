__author__ = 'weinan'

import math
import config

def win_sam(bid, l):
    return bid * 1. / (bid + l)

def win_ortb3(bid, l):
    return 1. - math.exp(- bid / l)


data_folder = "../../make-ipinyou-data/"
output_folder = "../exp-data/"
campaigns = config.campaigns
bid_upper = 300

bid_num = {}
for bid in range(0, bid_upper + 1):
    bid_num[bid] = 0

fo = open(output_folder + "market-prices.txt", "w")
for cam in campaigns:
    print "read in " + cam
    fi = open(data_folder + cam + "/train.yzpc.txt", "r")
    for line in fi:
        mp = int(line.split("\t")[1])
        bid_num[mp] += 1
        fo.write(str(mp) + "\n")
    fi.close()
fo.close()

print "calculating bid landscape"
sum = 0
for bid in bid_num:
    sum += bid_num[bid]

fo = open(output_folder + "bid_landscape.txt", "w")
bid_win = {}
acc = 0.
for bid in range(0, bid_upper + 1):
    acc += bid_num[bid]
    bid_win[bid] = acc / sum
    fo.write("%d\t%.6f\n" % (bid, acc / sum))
fo.close()

print "regression"
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

print "bid landscape " + str(campaigns)
print "optimal l: " + str(optimal_l) + "\tloss: " + str(min_loss / bid_upper)

