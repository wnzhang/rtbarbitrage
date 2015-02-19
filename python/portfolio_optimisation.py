__author__ = 'weinan'

# The risk-return trade-off of section 8.4 (Quadratic programming).

from math import sqrt
from math import exp
from cvxopt import matrix
from cvxopt.blas import dot
from cvxopt.solvers import qp, options
import pylab
import config
import numpy
import random

def solve_portfolio_with_cam_correlation(cam_mu, cam_sigma, cam_cor, alpha):
    n = len(cam_mu)
    cams = []
    cam_idx = {}
    idx_cam = {}
    idx = 0
    for cam in sorted(cam_mu):
        cams.append(cam)
        cam_idx[cam] = idx
        idx_cam[idx] = cam
        idx += 1
    mu = matrix(0.0, (n, 1))
    for cam in cams:
        mu[cam_idx[cam]] = cam_mu[cam]
    Sigma = matrix(0.0, (n, n))
    for cam1 in cams:
        idx1 = cam_idx[cam1]
        for cam2 in cams:
            idx2 = cam_idx[cam2]
            idx = idx1 * n + idx2
            cor = 0.0
            if (cam1, cam2) in cam_cor:
                cor = cam_cor[(cam1, cam2)]
            elif (cam2, cam1) in cam_cor:
                cor = cam_cor[(cam2, cam1)]
            Sigma[idx] = cor * cam_sigma[cam1] * cam_sigma[cam2]
    v = solve_portfolio(mu, Sigma, alpha)
    cam_v = {}
    for cam in cams:
        cam_v[cam] = v[cam_idx[cam]]

    config.cached_mu = mu
    config.cached_Sigma = Sigma
    config.cached_idx_cam = idx_cam.copy()
    config.cached_portfolio_sigma = sqrt(dot(v, Sigma * v))
    config.cached_cam_v = cam_v.copy()

    return cam_v

def solve_portfolio(mu, Sigma, alpha):
    # solve max_v mu^T * v - alpha * v^T * Sigma * v
    #       st    v >= 0
    #             sum(v) = 1
    (row, col) = Sigma.size
    (dim, one) = mu.size
    if row != col or dim != col or one != 1:
        print "portfolio dim error: %d %d %d %d" % (row, col, dim, one)
    n = row
    # we don't need to change the below setting
    G = matrix(0.0, (n,n))
    G[::n+1] = -1.0
    h = matrix(0.0, (n,1))  # G and h: -x <= 0 i.e. x >= 0
    A = matrix(1.0, (1,n))
    b = matrix(1.0)  # A and b: sum(x) = 1

    # optimise
    options['show_progress'] = False
    v = qp(alpha * Sigma, -mu, G, h, A, b)['x']
    return v

def efficient_frontier(mu, Sigma):
    (row, col) = Sigma.size
    (dim, one) = mu.size
    if row != col or dim != col or one != 1:
        print "portfolio dim error: %d %d %d %d" % (row, col, dim, one)
    n = row
    # we don't need to change the below setting
    G = matrix(0.0, (n,n))
    G[::n+1] = -1.0
    h = matrix(0.0, (n,1))  # G and h: -x <= 0 i.e. x >= 0
    A = matrix(1.0, (1,n))
    b = matrix(1.0)  # A and b: sum(x) = 1

    # Compute trade-off.
    N = 200
    alphas = [ 10**(5.0*t/N-1.0) for t in range(N) ]
    portfolios = [ qp(alpha * Sigma, -mu, G, h, A, b)['x'] for alpha in alphas ]
    returns = [ dot(mu, x) for x in portfolios ]
    risks = [ sqrt(dot(x, Sigma * x)) for x in portfolios ]
    return (returns, risks)

def draw_portfolio(mu, Sigma, idx_cam, portfolio_sigma):

    #Sigma = matrix( [[ 4e-2,  6e-3, -4e-3,   0.0 ],
    #             [ 6e-3,  1e-2,  0.0,    0.0 ],
    #             [-4e-3,  0.0,   2.5e-3, 0.0 ],
    #             [ 0.0,   0.0,   0.0,    0.0 ]] ) # covariance matrix
    #mu = matrix([.12, .10, .07, .03]) # mean vector

    mus = []
    sigmas = []
    n = Sigma.size[0]
    min_sigma = 1E90
    max_sigma = -1
    for i in range(n):
        sigmas.append(sqrt(Sigma[i*n + i]))
        if sqrt(Sigma[i*n + i]) > max_sigma:
            max_sigma = sqrt(Sigma[i*n + i])
        if sqrt(Sigma[i*n + i]) < min_sigma:
            min_sigma = sqrt((Sigma[i*n + i]))
    max_mu = -1
    min_mu = 1E90
    for i in range(n):
        mus.append(mu[i])
        if mu[i] > max_mu:
            max_mu = mu[i]
        if mu[i] < min_mu:
            min_mu = mu[i]

    # print max_sigma, max_mu

    # we don't need to change the below setting
    G = matrix(0.0, (n,n))
    G[::n+1] = -1.0
    h = matrix(0.0, (n,1))  # G and h: -x <= 0 i.e. x >= 0
    A = matrix(1.0, (1,n))
    b = matrix(1.0)  # A and b: sum(x) = 1

    # Compute trade-off.
    N = 200 # 100
    alphas = [ 10**(5.0*t/N-3.0) for t in range(N) ]
    options['show_progress'] = False
    portfolios = [ qp(alpha*Sigma, -mu, G, h, A, b)['x'] for alpha in alphas ]
    returns = [ dot(mu,x) for x in portfolios ]
    risks = [ sqrt(dot(x, Sigma*x)) for x in portfolios ]

    # sample portfolios
    M = 4000
    prisks = []
    preturns = []
    for i in range(M):
        w = []
        sum = 0.
        for j in range(n):
            weight = exp(random.random() * 6)
            w.append(weight)
            sum += weight
        for j in range(n):
            w[j] /= sum

        wv = matrix(w)
        pmu = dot(wv, mu)
        pstdev = sqrt(dot(wv, Sigma * wv))
        prisks.append(pstdev)
        preturns.append(pmu)

    # Plot trade-off curve and optimal allocations.
    pylab.figure(1, facecolor='w')
    pylab.plot(prisks, preturns, '.', color = '#6FCCF7', label='possible portfolio')
    pylab.plot(sigmas, mus, 'bo', label='individual campaign')
    pylab.plot(risks, returns, '-k', label='efficient frontier')
    pylab.xlabel('standard deviation')
    pylab.ylabel('expected return')
    pylab.axis([min(risks) * 0.9, max(risks) * 1.1, min_mu * 0.8, max_mu * 1.2])
    pylab.title('Risk-return of campaign portfolio')
    pylab.legend(loc='upper left')
    #pylab.yticks([0.00, 0.05, 0.10, 0.15])
    for i in range(n):
        pylab.text(sigmas[i] + (max_sigma-min_sigma)/70., mus[i], idx_cam[i])

    pylab.plot([portfolio_sigma, portfolio_sigma], [min_mu * 0.8, max_mu * 1.2], ":k")

    pylab.savefig(config.portfolio_efficient_frontier)
    pylab.clf()

    pylab.figure(1, facecolor='w')
    pacc = {}
    bottom = {}
    for c in range(n):
        pacc[c] = []
        for i in range(len(portfolios)):
            if i not in bottom:
                bottom[i] = 0
            pacc[c].append(bottom[i] + portfolios[i][c])
            bottom[i] = bottom[i] + portfolios[i][c]


    c_color = {0:'#F0F0F0', 1: "#A7D3F2", 2: "#F47979", 3: "#2AFF87", 4: "#FFFD9F", 5: "D14FEE"}

    for c in range(n):
        if c == 0:
            pylab.fill(risks + [min_sigma, max_sigma], pacc[c] + [0.0, 0.0], c_color[0])
        else:
            pylab.fill(risks[-1::-1] + risks, pacc[c][-1::-1] + pacc[c-1], facecolor = c_color[c])

    pylab.axis([min_sigma, max_sigma, 0.0, 1.0])
    pylab.xlabel('standard deviation')
    pylab.ylabel('allocation')

    #linex = [min_sigma + (max_sigma - min_sigma) / 3.0, min_sigma + (max_sigma - min_sigma) / 3.0]
    pylab.plot([portfolio_sigma, portfolio_sigma], [0, 1], ":k")

    start_risk = {}
    end_risk = {}
    thres = 1E-2
    for c in range(n):
        start_risk[c] = -1
        end_risk[c] = -1
        for i in range(N):
            b = 0
            if c > 0:
                b = pacc[c-1][i]
            if start_risk[c] == -1 and pacc[c][i] - b > thres:
                start_risk[c] = i
            if start_risk[c] != -1 and pacc[c][i] - b < thres:
                end_risk[c] = i
        if end_risk[c] == -1:
            end_risk[c] = N-1

        #print "c" + str(c+1) + " start risk: " + str(risks[start_risk[c]])
        #print "c" + str(c+1) + " end risk: " + str(risks[end_risk[c]])

        lx = (risks[start_risk[c]] + risks[end_risk[c]]) / 2.
        idx = 0
        for i in range(N - 1):
            if (risks[i] - lx) * (risks[i+1] - lx) < 0:
                idx = i
                break
        b = 0
        if c > 0:
            b = pacc[c-1][idx]
        ly = (pacc[c][idx] + b) / 2.
        pylab.text(lx, ly, idx_cam[c])

    pylab.title('Campaign allocations')
    #pylab.show()
    pylab.savefig(config.portfolio_campaign_allocation)

def test():

    Sigma = matrix([[ 21.5231858537, 0.0, 0.0, 0.0,],
		[ 0.0, 0.0232300684934, 0.0, 0.0,],
		[ 0.0, 0.0, 21.1067129846, 0.0,],
		[ 0.0, 0.0, 0.0, 3.91434863659,],
		])
    mu = matrix([ 13.3532827721, 1.80228043117, 9.98270327181, 4.63560884383,])
    idx_cam = {0: '3358', 1: '3386', 2: '3427', 3: '3476'}
    portfolio_sigma = 4.4 # 3.42380649286

    draw_portfolio(mu, Sigma, idx_cam, portfolio_sigma)

#test()