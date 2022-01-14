"""Функции для расчёта задержки воспламенения средствами Кантеры"""

import cantera as ct
import numpy as np

def run_ign(model: str, T: float, p: float, phi: float=0.5) -> ct.SolutionArray:
    gas = ct.Solution(model)
    gas.TP=T,p*101325.0 #,f'O2: 0.21, N2: 0.78, AR: 0.01, CH4: {xn}'
    gas.set_equivalence_ratio(phi=phi, fuel='CH4', oxidizer={'O2': 0.21, 'N2': 0.79 }) ##  'Ar': 0.01
    r = ct.ConstPressureReactor(contents=gas)
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
    tT = (states.t[i_ign]+states.t[i_ign+1])/2
    i_oh = np.argmax(states('OH').X)
    return {'dT/dt': tT, 'oh': states.t[i_oh]}
