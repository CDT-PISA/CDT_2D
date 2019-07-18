def new_fit(fit_name):
    pass

def set_fit_sims(fit_name, sims):
    pass

def cut_block():
    pass

def volume_fit(fit_name):
    import json
    from numpy import sqrt, log, zeros, diag, vectorize

    # dt.datetime.strptime(state['end_time'], '%d-%m-%Y %H:%M:%S')

    lambdas = array(lambdas_old)
    volumes = array(volumes)
    errors = array(errors)

    fig = figure()
    ax = fig.add_subplot(111)

    ax.errorbar(lambdas, volumes, yerr=errors, fmt='none', capsize=5)

    def volume(l, l_c, alpha, A):
        return A*(l - l_c)**(-alpha)

    par, cov = curve_fit(volume, lambdas, volumes, sigma=errors, absolute_sigma=True,
                         p0=(0.69315, 2.4, 61))

    residuals_sq = ((volumes - vectorize(volume)(lambdas, *par))/errors)**2
    chi2 = residuals_sq.sum()
    dof = len(lambdas) - len(par)

    print("χ² = ", chi2, dof)

    names = ['λ_c', 'alpha', 'factor']#, 'shift']
    print(dict(zip(names, par)))
    print(dict(zip(names,sqrt(diag(cov)))))

    n = len(par)
    corr = zeros((n, n))
    for i in range(0, n):
        for j in range(0, n):
            corr[i,j] = cov[i,j]/sqrt(cov[i,i]*cov[j,j])

    print(corr)

    l_inter = linspace(min(lambdas), max(lambdas), 1000)
    ax.plot(l_inter, volume(l_inter, *par))

    show()
