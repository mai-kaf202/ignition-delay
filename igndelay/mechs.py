"""Обзор присутствующих механизмов"""
import os
from typing import NamedTuple, Optional, Iterator
from cantera.ck2yaml import Parser

OldCkMech = NamedTuple('OldCkMech', [('mech', str), ('therm', str), ('tran', Optional[str])])
CKMech = NamedTuple('CKMech', [('gas', str), ('gtran', str)])


def find_mechs(root:str = 'mechanisms') -> dict[str, OldCkMech]:
    ret : dict[str, OldCkMech] = {}
    for mechdir in os.scandir(root):
        indir = mk_mechs(os.scandir(mechdir))
        if len(indir) == 1:
            ret[mechdir.name] = indir[0][1]
        else:
            ret.update(dict(indir))
    return ret

def mk_mechs(it: Iterator[os.DirEntry]) -> list[tuple[str, OldCkMech]]:
    fs = [x for x in it]
    therms = [x for x in fs if 'therm' in x.name.lower()]
    transs = [x for x in fs if 'tran' in x.name.lower()]
    mechs =  [x for x in fs if ('tran' not in x.name.lower()) and ('therm' not in x.name.lower()) and ('.bak' not in x.name.lower())]
    trans = transs[0].path if len(transs)==1 else None
    therm = therms[0].path if len(therms)==1 else None
    if len(therms)>1:
        print('NOTE: too many thermodatas')
    return [(m.name.split('.')[0], OldCkMech(m.path, therm, trans)) for m in mechs]

def cantera_conv(name: str, mech: OldCkMech, root:str='instance/mechs') -> str:
    if not os.path.exists(root):
        os.mkdir(root)
    tgtfn = f'{root}/{name}.yaml'
    if not os.path.exists(tgtfn):
        Parser.convert_mech(mech.mech, mech.therm, mech.tran, None, 'gas', None, tgtfn, True, True)
    return tgtfn

if not os.path.exists('instance'):
    os.mkdir('instance')