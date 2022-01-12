"""Служебные функции для работы с экспериментами по самовоспламенению"""
import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def run_ign(model: str, T: float, p: float, phi: float=0.5) -> ct.SolutionArray:
    gas = ct.Solution(model)
    gas.TP=T,p*101325.0 #,f'O2: 0.21, N2: 0.78, AR: 0.01, CH4: {xn}'
    gas.set_equivalence_ratio(phi=phi, fuel='CH4', oxidizer={'O2': 0.21, 'N2': 0.79 }) ##  'Ar': 0.01
    r = ct.Reactor(contents=gas)
    reactorNetwork = ct.ReactorNet([r])
    timeHistory_RG = ct.SolutionArray(gas, extra=['t'])
    t=0
    estimatedIgnitionDelayTime = 0.0005

    while t < estimatedIgnitionDelayTime:
        t = reactorNetwork.step()
        # We will save only every 20th value. Otherwise, this takes too long
        # Note that the species concentrations are mass fractions
        timeHistory_RG.append(r.thermo.state, t=t)
    return timeHistory_RG

def ignitionDelay(states):
    i_ign = (np.diff(states.T)/np.diff(states.t)).argmax()
    return states.t[i_ign]

def experimental(filename='data/experimental.txt') -> pd.DataFrame:
    f = open(filename, encoding='utf-8')
    ds = [x.strip().split('\t') for x in f]
    f.close()
    indata = [(float(a.replace(',','.')), float(b), *[float(w) for w in c.split('±')], float(d)) for [a,b,c,d] in ([x[:4] for x in ds[1:]] + [x[4:] for x in ds [1:]])]
    return pd.DataFrame(indata, columns=['p, атм', 'T, K', 't_эксп, мкс', 'Δt_эксп, мкс', 't_calc, мкс'])