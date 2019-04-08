# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 11:32:00 2019

@author: alessandro
"""

from numpy import loadtxt
from matplotlib.pyplot import plot, imshow, colorbar, figure, savefig, subplots, subplots_adjust, close

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

def select_from_plot(Lambda, indices, volumes, i):
    from matplotlib.pyplot import figure, show, figtext
    
    imin = indices[0]
    imax = indices[-1]
    vmin = min(volumes)
    vmax = max(volumes)
    
    color_cycle = ['xkcd:carmine', 'xkcd:teal', 'xkcd:peach', 'xkcd:mustard',
                   'xkcd:cerulean']
    
    n_col = len(color_cycle)
    
    fig = figure()
    ax = fig.add_subplot(111)
    canvas = fig.canvas
    
    fig.set_size_inches(7, 5)
    ax.plot(indices, volumes, color=color_cycle[i % n_col])
    ax.set_title('λ = ' + str(Lambda))
    figtext(.5,.03,' '*10 + 
            'press enter to convalid current selection', ha='center')
    fig.canvas.draw()
    
    def on_click(event):
        if event.inaxes is not None:
            x = event.xdata
            y = event.ydata
            inarea = x > imin and x < imax and y > vmin and y < vmax
            if inarea:
                on_click.x = x
                if on_click.i > 0:
                    on_click.m[0].remove()
                on_click.m = ax.plot(x, y, 'o', mec='w')
                event.canvas.draw()
                on_click.i += 1
    on_click.i = 0
    on_click.m = None
    on_click.x = 0
        
    def on_motion(event):
        if event.inaxes is not None:
            x = event.xdata
            y = event.ydata
            inarea = x > imin and x < imax and y > vmin and y < vmax
            if inarea:
                m = ax.plot(x, y, 'wo', mec='k')
                n = ax.plot(x, vmin, 'k|', ms=20)
                event.canvas.draw()
                m[0].remove()
                n[0].remove()
        
    def on_key(event):
        if event.key == 'enter':
            close()
    
    canvas.mpl_connect('button_release_event', on_click)
    canvas.mpl_connect('motion_notify_event', on_motion)
    canvas.mpl_connect('key_press_event', on_key)
    show()
    
    return on_click.x
            

def fit(lambdas_old, config, force):
    import readline
    from numpy import loadtxt
    
    i = -1
    for Lambda in lambdas_old:
        i += 1
        
        vol_file = ('output/' + config + '/Lambda' + str(Lambda) +
                   '/history/volumes.txt')
        indices, volumes = loadtxt(vol_file, unpack=True)
#        imin = indices[0]
#        imax = indices[-1]
        vmin = min(volumes)
        vmax = max(volumes)
        
        print("Select the x cut ('p' for plot or type it, or just ENTER to use"
                                 + " a previous choice)")
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
                    if choice < vmin or choice >= vmax:
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
            cut = select_from_plot(Lambda, indices, volumes, i)
        elif choice == 'stored':
            print("Me lo vado a prendere nel json")
            old_found = False
            if not old_found:
                cut = select_from_plot(Lambda, indices, volumes, i)
                
        print('E ora lo conservo nel json')
        volumes = volumes[indices < cut]
        print(len(volumes)/len(indices))