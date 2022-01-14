"""Служебные функции для работы с экспериментами по самовоспламенению"""
import pandas as pd
import os

def experimental(filename='data/experimental.txt') -> pd.DataFrame:
    f = open(filename, encoding='utf-8')
    ds = [x.strip().split('\t') for x in f]
    f.close()
    indata = [(float(a.replace(',','.')), float(b), *[float(w) for w in c.split('±')], float(d)) for [a,b,c,d] in ([x[:4] for x in ds[1:]] + [x[4:] for x in ds [1:]])]
    return pd.DataFrame(indata, columns=['p, атм', 'T, K', 't_эксп, мкс', 'Δt_эксп, мкс', 't_calc, мкс'])

def workdir() -> str:
    """Текущая рабочая папка"""
    WORKPATH='./instance/ckwork'
    if not os.path.exists(WORKPATH):
        os.mkdir(WORKPATH)
    return WORKPATH