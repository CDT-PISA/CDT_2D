#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 11:32:00 2019

@author: alessandro
"""

from numpy import loadtxt
from matplotlib.pyplot import plot, imshow, colorbar, figure, savefig, subplots, subplots_adjust, close

def analyze_output(outdir):
    """Output analysis for CDT_2D simulation.
    
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
    im = ev.imshow(space_profiles.transpose(), cmap="hot", interpolation='bilinear', origin="lower", aspect="auto")
    fig2.colorbar(im,cax=ax2)
    
    ev.grid(False)
    ev.get_xaxis().set_visible(False)
    aux.axis("off")
    fig2.suptitle("Titolo", fontsize=20, y=0.95)
    
    savefig(outdir+"/space_profile_evolution.png")
    close(fig2)
    
#    si potrebbe pensare di stampare almeno un paio di profili spaziali insieme, magari non vicini (entrambi nella parte finale, così che siano ben termalizzati, ma non vicini in modo che siano il meno possibile correlati) per analizzare l'andamento dell'evoluzione
#    ma in realtà forse no: si vede già dal secondo plot
#
#    figure(1)
#    subplot(212)
#    plot(space_profiles[-10])
    
#    close("all")
    
    return