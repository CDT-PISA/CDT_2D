
from numpy import loadtxt
from matplotlib.pyplot import plot, imshow, colorbar, figure, savefig, subplots, subplots_adjust, close
from __init__ import select_from_plot

def analyze_output(outdir):
    """Output analysis for CDT_2D simulation.
    attempts_str = str(attempts)

    Descrizione...

    Parameters
    ----------
    p1 : tipo
        descrizione del primo parametro p1
    p2 : tipo
        descrizione del secondo parametro p2
    p3 : tipo, optional
        descrizione del terzo parametro opzionale p3

    Returns
    -------
    tipo
        descrizione del tipo di ritorno

    Raises
    ------
    Exception
        descrizione dell'eccezione lanciata
    """
    print("Run",outdir.split("run")[1])

    space_profiles = loadtxt(outdir+"/simulation_output",unpack=False)
    print(space_profiles[-1])

    # figure1 represents a snapshot of the spacetime near the end of simulation
    fig1 = figure()
    plot(space_profiles[-1])

    fig1.suptitle("Titolo", fontsize=20, y=0.95)

    savefig(outdir+"/space_profile_thermalized.png")
    close(fig1)

    # figure2 represents the evolution in simulation time
    kw = {'height_ratios':[4,1], "width_ratios":[97,3]}
    fig2, ((ev, ax2),(sm,aux)) = subplots(2,2,  gridspec_kw=kw)
    sm.get_shared_x_axes().join(ev, sm)
    subplots_adjust(bottom=0.05,top=0.89,left=0.07,right=0.95,hspace=0.05,wspace=0.05)
    sm.plot(space_profiles.sum(1),color="#A10000")
    im = ev.imshow(space_profiles.transpose(), cmap="hot", interpolation=None, origin="lower", aspect="auto")
    #'bilinear'
    fig2.colorbar(im,cax=ax2)

    ev.grid(False)
    ev.get_xaxis().set_visible(False)
    aux.axis("off")
    fig2.suptitle("Titolo", fontsize=20, y=0.95)

    savefig(outdir+"/space_profile_evolution.png")
    close(fig2)

    # per imshow devo assicurarmi che siano equispaziati!

#    si potrebbe pensare di stampare almeno un paio di profili spaziali insieme,
#    magari non vicini (entrambi nella parte finale, così che siano ben termalizzati,
#    ma non vicini in modo che siano il meno possibile correlati) per analizzare
#    l'andamento dell'evoluzione
#    ma in realtà forse no: si vede già dal secondo plot
#
#    figure(1)
#    subplot(212)
#    plot(space_profiles[-10])

#    close("all")


# def funzione per controllare se è termalizzato  (fit bayesiano o ANOVA)

def is_thermalized():
    return False

def fit(lambdas_old, config, skip):
    from os import chdir, getcwd
    import json
    from numpy import array, linspace
    from matplotlib.pyplot import figure, show
    from scipy.optimize import curve_fit

    proj_dir = getcwd()
    volumes = []
    errors = []
    if skip == False:
        import readline
        from numpy import loadtxt

        i = -1
        for Lambda in lambdas_old:
            i += 1
            chdir('output/' + config + '/Lambda' + str(Lambda))

            vol_file = ('history/volumes.txt')
            indices, volumes = loadtxt(vol_file, unpack=True)
            imin = indices[0]
            imax = indices[-1]
            vmin = min(volumes)
            vmax = max(volumes)

            print("[ λ = " + str(Lambda) + " ]")
            print("Select the x cut ('p' for plot or type it, or just ENTER"
                                     + " to use a previous choice)")
            valid = False
            count = 0
            while not valid and count < 3:
                count += 1
                try:
                    choice = input('--> ')
                except EOFError:
                    choice = ''
                    print()

                valid = True
                if choice == 'q' or choice == 'quit':
                    choice = 'q'
                elif choice == 'p':
                    choice = 'plot'
                elif choice == '':
                    choice = 'stored'
                else:
                    try:
                        choice = int(choice)
                        if choice < imin or choice >= imax:
                            raise ValueError
                    except ValueError:
                        valid = False
                        print('Answer not valid', end='')
                        if count < 3:
                            print(', type it a valid one')
                        else:
                            choice = 'q'
                            print(' (nothing done)')

            with open('state.json', 'r') as state_file:
                state = json.load(state_file)

            if choice == 'q':
                print('Nothing done, restart from the beginning')
                return
            elif type(choice) == int:
                cut = choice
            elif choice == 'plot':
                cut, height = select_from_plot(Lambda, indices, volumes, i)
                if cut == None:
                    print('Nothing done, restart from the beginning')
                    return
                elif cut == -1:
                    print('Using the default one.')
                    choice = 'stored'
            if choice == 'stored':
                try:
                    cut = state['cut']
                    height = (vmax + vmin) / 2
                except KeyError:
                    print('Default cut not found, select it on the plot.')
                    cut, height = select_from_plot(Lambda, indices, volumes, i)

            state['cut'] = cut
            volumes_cut = volumes[indices > cut]
            indices_cut = indices[indices > cut]

            dot = (cut, height)

            def blocked_mean_std(indices, volumes, block_size):
                from numpy import mean, std
                from math import sqrt

                bs = block_size
                buffer_start = indices[0]
                buffer = []
                block_means = []
                for i in range(0,len(indices)):
                    if (indices[i] - buffer_start) > bs:
                        block_means += [mean(buffer)]
                        buffer = []
                        buffer_start = indices[i]
                    buffer += [volumes[i]]

                vol = mean(block_means)
                err = std(block_means) / sqrt(len(block_means) - 1)

                return vol, err

            print("Select the x blocking ('p' for plot, 'b' for blocks' " +
                  "plot or type it, or just ENTER to use a previous choice)")
            valid = False
            count = 0
            while not valid and count < 3:
                count += 1
                try:
                    choice = input('--> ')
                except EOFError:
                    choice = ''
                    print()

                valid = True
                if choice == 'q' or choice == 'quit':
                    choice = 'q'
                elif choice == 'p':
                    choice = 'plot'
                elif choice == 'b':
                    choice = 'blocks plot'
                elif choice == '':
                    choice = 'stored'
                else:
                    try:
                        choice = int(choice)
                        if choice < 1 or choice >= (imax - cut):
                            raise ValueError
                    except ValueError:
                        valid = False
                        print('Answer not valid', end='')
                        if count < 3:
                            print(', type it a valid one')
                        else:
                            choice = 'q'
                            print(' (nothing done)')

            if choice == 'q':
                print('Nothing done, restart from the beginning')
                return
            elif choice == 'plot':
                x_sel, _ = select_from_plot(Lambda, indices, volumes, i, dot)
                if x_sel == None:
                    print('Nothing done, restart from the beginning')
                    return
                elif x_sel == -1:
                    print('Using the default one.')
                    choice = 'stored'
                block = x_sel - cut
            if choice == 'stored':
                try:
                    block = state['block']
                except KeyError:
                    print('Default block size not found, ' +
                          'select it on the plot.')
                    choice = 'blocks plot'
            if choice == 'blocks plot':
                from math import log

                block_sizes = [2**k for k in
                               range(0, int(log(imax - cut, 2)) - 3)]
                stdevs = []
                for bs in block_sizes:
                    _, stdev = blocked_mean_std(indices_cut, volumes_cut, bs)
                    stdevs += [stdev]

                block, _ = select_from_plot(Lambda, block_sizes, stdevs, i)
                if block == None or block == -1:
                    print('Nothing done, restart from the beginning')
                    return
                block = int(block)

            state['block'] = block

            vol, err = blocked_mean_std(indices_cut, volumes_cut, block)

            state['asymptotic mean volume'] = (vol,err)
            volumes += [vol]
            errors += [err]

            with open('state.json', 'w') as state_file:
                json.dump(state, state_file, indent=4)

            chdir(proj_dir)
    else:
        for Lambda in lambdas_old:
            chdir('output/' + config + '/Lambda' + str(Lambda))

            with open('state.json', 'r') as state_file:
                    state = json.load(state_file)

            try:
                volumes += [state['asymptotic mean volume'][0]]
                errors += [state['asymptotic mean volume'][1]]
            except KeyError:
                print('')
                print('Nothing done, restart from the beginning')
                return

            chdir(proj_dir)

    from numpy import sqrt, log, zeros, diag, vectorize

    lambdas = array(lambdas_old)
    volumes = array(volumes)
    errors = array(errors)

    fig = figure()
    ax = fig.add_subplot(111)

    print(errors.shape)
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
