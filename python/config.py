__author__ = 'weinan'

from math import sqrt
from cvxopt import matrix
from cvxopt.blas import dot
from cvxopt.solvers import qp, options
import pylab

print "import the parameters setting from config file"

# data
data_folder = "../../make-ipinyou-data/"
result_file = "../results/bttt/stage-2/arbitrage.results.txt"
portfolio_file = "../results/bttt/stage-2/arbitrage.multiple.txt"

single_campaign = "1458"
single_cam_bid_algorithms = ["const", "rand", "truth", "lin", "ortb", "sam1", "sam2"]

campaigns = ["2259", "2261", "2821", "2997"]# ["3358", "3386", "3427", "3476"] # ["3358", "3386", "3427", "3476"]

dsp_l = 42 # 48 # ["3358", "3386", "3427", "3476"] : 42

cam_l = {"1458": 34, "2259": 50, "2261": 47, "2821": 47, "2997": 28,
         "3358": 51, "3386": 39, "3427": 42, "3476": 41}

bid_algorithms = ["const", "rand", "truth", "lin", "ortb", "sam1", "sam2"]
volume = 300000
budget_proportions = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024] #, 2048, 4096, 8192, 16384] #[2, 4, 8, 16, 32, 64, 128, 256, 512, 1024] # 16, 64, 256]
algo_paras = {
    "const": range(5, 300, 18),
    "rand": range(5, 400, 24),
    "truth": [1],
    "lin": range(5, 150, 5),
    "ortb": [1 * t for t in range(20, 1400, 30)],
    "sam1": range(5, 150, 4),
    "sam2": [0.1 * t for t in range(1, 100, 2)],
    }

algo_one_para = {
    "const": 100,
    "rand": 100,
    "truth": [1],
    "lin": 50,
    "ortb": 800,
    "sam1": 100,
    "sam2": 5,
    }

cm_up_value = 0.

cpc_payoff_ratio = 0.8  # set the cpc payoff for click click as original ecpc * cpc_payoff_ratio

M = len(campaigns)  # num of campaigns

# em part
em_rounds = 2

# e-step
alpha = 0.001
#alphas = ["uniform", 0.001, 0.01, 0.1, 0.2, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]  #"uniform",
alphas = ["uniform", 0.001, 0.00316, 0.01, 0.0316, 0.1, 0.316, 1, 10, 100, 1000]  #"uniform",

e_step_mu_process_num = 10

cached_Sigma = matrix([])
cached_mu = matrix([])
cached_idx_cam = {}
cached_portfolio_sigma = 0
cached_cam_v = {}

# m-step

# portfolio figures
portfolio_efficient_frontier = "../results/stage-2-portfolio-efficient-frontier.pdf"
portfolio_campaign_allocation = "../results/stage-2-portfolio-campaign-allocation.pdf"


# stage-3
stage_3_budget_proportion = 2
stage_3_alpha = 1 #0.2
stage_3_algo = "sam2"
stage_3_round_hour = 3

def print_cached_Sigma_mu():
    n = cached_Sigma.size[0]
    sigma_str = "\tSigma = matrix(["
    for i in range(n):
        sigma_str = sigma_str + "["
        for j in range(n):
            sigma_str = sigma_str + " " + str(cached_Sigma[i*n + j]) + ","
        sigma_str = sigma_str + "],\n\t\t"
    sigma_str = sigma_str + "])"
    print sigma_str

    mu_str = "\tmu = matrix(["
    for i in range(n):
        mu_str = mu_str + " " + str(cached_mu[i]) + ","
    mu_str = mu_str + "])"
    print mu_str

    idx_cam_str = "\tidx_cam = " + str(cached_idx_cam)
    print idx_cam_str

    portfolio_sigma_str = "\tportfolio_sigma = " + str(cached_portfolio_sigma)
    print portfolio_sigma_str


def write_cached_Sigma_mu(fpo):
    n = cached_Sigma.size[0]
    sigma_str = "\tSigma = matrix(["
    for i in range(n):
        sigma_str = sigma_str + "["
        for j in range(n):
            sigma_str = sigma_str + " " + str(cached_Sigma[i*n + j]) + ","
        sigma_str = sigma_str + "],\n\t\t"
    sigma_str = sigma_str + "])"
    fpo.write(sigma_str + "\n")

    mu_str = "\tmu = matrix(["
    for i in range(n):
        mu_str = mu_str + " " + str(cached_mu[i]) + ","
    mu_str = mu_str + "])"
    fpo.write(mu_str + "\n")

    idx_cam_str = "\tidx_cam = " + str(cached_idx_cam)
    fpo.write(idx_cam_str + "\n")

    portfolio_sigma_str = "\tportfolio_sigma = " + str(cached_portfolio_sigma)
    fpo.write(portfolio_sigma_str + "\n")

    cam_v_str = "\tcam_v = " + str(cached_cam_v)
    fpo.write(cam_v_str + "\n")
