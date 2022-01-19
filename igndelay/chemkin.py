from typing import NamedTuple
import subprocess
from os import path
import time
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np

from .mechs import CKMech, OldCkMech
from . import workdir
from binascii import crc32

CKEnv = NamedTuple('CKEnv', [('bin', str)])

test_env = CKEnv(r"E:\Soft\ANSYS Inc\v172\reaction\chemkinpro.win64\bin")

def run_ck_psr(env: CKEnv, mech: CKMech, T: float, p: float) -> pd.DataFrame:
    """Рассчитывает кемкином Perfectly Stirred Reactor (0D)"""
    config = f"""ENRG
    TRAN
    EQUI 0.5
    PRES {p}
    QLOS 0.0
    TEMP {T}
    CPROD CO2
    CPROD H2O
    CPROD N2
    FUEL CH4 1.0
    OXID N2 0.79
    OXID O2 0.21
    ADAP
    TIME 0.0005
    GFAC 1.0
    END"""
    return run_ck(env, mech, 'CKReactorGenericClosed', config)

def run_ck_refl(env: CKEnv, mech: CKMech, T: float, p: float) -> pd.DataFrame:
    config = f"""RSHK
    EQUI 0.5
    P3A {p}
    T3 {T}
    VSHK 1.2E5
    CPROD CO2
    CPROD H2O
    CPROD N2
    FUEL CH4 1.0
    OXID N2 0.79
    OXID O2 0.21
    TIME 0.0005
    TSTR 0.0
    END"""
    return run_ck(env, mech, 'CKReactorReflectedShock', config)

def run_ck(env: CKEnv, mech: CKMech, selbin: str, inpfile: str) -> pd.DataFrame:
    binary = path.join(env.bin, selbin)
    pref = workdir()
    hash = crc32(inpfile.encode('utf-8'))
    inp_fn = path.join(pref, f'{hash}.inp')
    f = open(inp_fn, 'w')
    f.write(inpfile)
    f.close()
    outxml = path.join(pref, f'{hash}.zip')
    args = [binary, "-i", path.realpath(inp_fn), 
    "-x", path.realpath(outxml), "Pro",
    "-c", path.realpath(mech.gas),
    "-o", path.realpath(f'{pref}/{hash}.out'),
    "-t", path.realpath(mech.gtran)]
    sp = subprocess.run(args, cwd='instance/ckwork')
    if sp.stdout:
        f = open(f'{pref}/{hash}.std', 'w')
        f.write(sp.stdout)
        f.close()
    if sp.stderr:
        f = open(f'{pref}/{hash}.err', 'w')
        f.write(sp.stderr)
        f.close()
    time.sleep(0.5)
    return ck_parse_results(outxml)

def ck_parse_results(xmlfn: str)->pd.DataFrame:
    ret = []
    with ZipFile(xmlfn) as zf:
        tgtfns = [v for v in [x.filename for x in zf.filelist] if v.split('.')[0][-2:] in ['_2', '_3']]
        xmlfs = [tgt.read(tgt.filelist[0].filename).decode() for tgt in [ZipFile(BytesIO(zf.read(fn))) for fn in tgtfns]]
        xmlf = xmlfs[0].replace('<EOF>', xmlfs[1].split('</ENDTOF>')[1]) if len(xmlfs)>1 else xmlfs[0]
    ckd = ET.fromstring(xmlf.replace('<TOF>','').replace('<EOF>',''))
    MASSFRACS = ['CH4', 'OH']
    VARS = ['temperature']
    patt = [(v, f"./*/[@name='{v}']/statevalue") for v in VARS]
    patt += [(v, f"./*/[speciesid='{v}']/statevalue") for v in MASSFRACS]
    patt += [('time', "./timevalue")]
    ret += [{k: float(t.findall(z)[0].text) for (k, z) in patt} for t in ckd.iter('timepoint')]
    return pd.DataFrame(ret)

def ck_ign(df: pd.DataFrame) -> dict[str, float]:
    t = df['time']
    idT = np.argmax(np.diff(df['temperature'])/np.diff(t))
    tT = (t[idT]+t[idT+1])/2
    oh = t[np.argmax(df['OH'])]
    return {'dT/dt': tT, 'OHmax': oh}

def chemkin_conv(name: str, mech: OldCkMech, env: CKEnv = test_env, root: str = 'instance/mechs'):
    fs = r"""IN_CHEM_INPUT=C:\code\work\ignition-delay\mechanisms\NUImech\NUIGMech1.1.MECH
IN_SURF_INPUT=
IN_THERM_DB=C:\code\work\ignition-delay\mechanisms\NUImech\NUIGMech1.1.THERM
IN_TRANS_DB=C:\code\work\ignition-delay\mechanisms\NUImech\NUIGMech1.1.TRAN
IN_LIQUID_DB=
FIT_TRANSPORT_PROPERTIES=0
OUT_CHEM_OUTPUT=C:\Users\emera\chemkin\test\nui_gas.out
OUT_CHEM_ASC=C:\Users\emera\chemkin\test\nui_gas.asc
OUT_CHEM_SPECIES=C:\Users\emera\chemkin\test\nui_gas.asu
OUT_SURF_OUTPUT=
OUT_SURF_ASC=
OUT_SURF_SPECIES=
OUT_TRAN_OUTPUT=C:\Users\emera\chemkin\test\nui_gtran.out
OUT_TRAN_ASC=C:\Users\emera\chemkin\test\nui_gtran.asc
OUT_XML_PARAMETERS=C:\Users\emera\chemkin\test\nui.xml
OUT_COMPOSITION=C:\Users\emera\chemkin\test\nui.cklmnt
OUT_REACTIONS=C:\Users\emera\chemkin\test\nui.cktab
"""
    pass