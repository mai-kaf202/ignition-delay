"""Вспомогательные процедуры для мультипроцессности"""

from typing import Any
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
