"""Вспомогательные процедуры для мультипроцессности"""

from typing import Any
import os
import numpy as np
import pandas as pd
from .cantera import run_ign, ignitionDelay
from .chemkin import run_ck_psr, run_ck_refl, ck_ign

def worker(a: tuple[str, Any]):
    (k, args) = a
    if k == 'CHg':
        return (*a, ck_ign(run_ck_psr(*args)))
    if k == 'REFL':
        return (*a, ck_ign(run_ck_refl(*args)))
    sarr = run_ign(*args)
    # ret = [sarr.t, sarr.T, sarr.P, sarr('CH4').X, sarr('CH4').Y, sarr('OH').X, sarr('OH').Y]
    return (*a, ignitionDelay(sarr))

def ct_calc(args: tuple[str, str, float, float]) -> pd.DataFrame:
    ROOT = 'instance/ct'
    if not os.path.exists(ROOT):
        os.mkdir(ROOT)
    [name, model, T, p] = args
    fn = f'{ROOT}/{name}_{T}K_{p}atm.dat'
    
    print(fn)
    delay = {}
    if not os.path.exists(fn):
        sarr = run_ign(model, T, p)
        df = pd.DataFrame({
            't': sarr.t,
            'T': sarr.T,
            'P': sarr.P, 
            'CH4': sarr('CH4').Y.T[0], 
            'OH': sarr('OH').Y.T[0]})
        df.to_pickle(fn)
    else:
        df = pd.read_pickle(fn)
    return df

def ct_worker(args: tuple[str, str, float, float]):
    df = ct_calc(args)
    [name, model, T, p] = args
    delay = df_ign_delay(df)
    return ((name, T, p), delay)

def df_ign_delay(df: pd.DataFrame) -> dict[str, float]:
    i_ign = (np.diff(df['T'])/np.diff(df['t'])).argmax()
    tT = (df['t'][i_ign]+df['t'][i_ign+1])/2
    i_oh = np.argmax(df['OH'])
    return {'dT/dt': tT, 'oh': df['t'][i_oh]}