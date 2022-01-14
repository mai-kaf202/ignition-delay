# Источники

Используются: Cantera v.;
ANSYS CHEMKIN Pro (17.2, 20.2)

## Механизмы

- ZhK CH4: [Zhukov, Kong, A compact reaction mechanism of methane oxidation at high pressures](https://doi.org/10.3184/146867818X15066862094914)
- GRI-Mech 3.0
- GRI-Mech 1.2
- USC C1-C3: [Qin et al., An Optimized Reaction Model of C1-C3 Combustion](http://ignis.usc.edu/Mechanisms/C3-opt/c3_opt.pdf)
- Aramco 1.3
- Aramco 2.0
- Aramco 3.0
    - NOTE: 5544..5569 of MECH file were edited: Chemkin parses +M & PLOG with PLOG prev.
- Zhukov C1-C7: [Zhukov, Kinetic model of alkane oxidation at high pressure from methane to n-heptane](https://www.researchgate.net/publication/225004510)
- Zhukov C1-C4
- RAMEC: [Peterson, Davidson, Hanson, Kinetics Modeling of Shock-Induced Ignition in Low-Dilution CH4/O2 Mixtures at High Pressures and Intermediate Temperatures](https://doi.org/10.1016/S0010-2180(98)00111-4)
- Slavinskaya
- NUIMech

## Препроцессинг
временно - в ручном виде

```bash
ck2yaml --input MECH --thermo THERM --trans TRANS
```