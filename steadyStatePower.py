# USAGE INSTRUCTIONS
# Execute.

import uncertainties
from uncertainties.umath import *
from math import pi
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")

# Uncertainty of R is 1%. I've calculated the exact value because it was simple.
# Converted scientific notation in my head.
L = uncertainties.ufloat(0.01525, 0.00002)
C = uncertainties.ufloat_fromstr('9.91(0.02)e-9')
Vs = uncertainties.ufloat(12, 0.1)

# Format is freqency, voltage, voltage_error
raw_data_100 = [(0.1,    0.0175, 0.0025),
                (1,      0.081,  0.002),
                (5,      0.46,   0.004),
                (8,      0.98,   0.004),
                (10,     1.9,    0.02),
                (12.96,  6,      0.08),
                (17,     1.52,   0.02),
                (20,     0.98,   0.02),
                (12,     5.28,   0.08),
                (14,     3.84,   0.02),
                (30,     0.416,  0.008),
                (40,     0.248,  0.004),
                (60,     0.068,  0.002),
                (80,     0.064,  0.002),
                (100,    0.158,  0.002),
                (13.54,  4.76,   0.04),
                (11,     3.08,   0.04),
                (11.52,  4.96,   0.04),
                (11.26,  3.48,   0.04),
                (11.435, 3.8,    0.04),
                (11.6,   4.2,    0.04)]


class SSDataPoint:
    def __init__(self, frequency, voltage, voltage_error, resistance):
        self.R = uncertainties.ufloat(resistance, 0.01*resistance)
        self.f = uncertainties.ufloat(frequency*1000, 0.01*1000*frequency)
        self.v = uncertainties.ufloat(voltage, voltage_error)
        self.w = 2 * pi * self.f
        # Current calculate from measurements
        self.I_m = self.v / self.R
        # Theoretical current
        Xc = 1/(self.w * C)
        Xl = self.w * L
        Xd = Xl-Xc
        Xq = pow(Xd, 2)
        Rq = pow(self.R, 2)
        denom = sqrt(Rq+Xq)
        # self.I_t = Vs / sqrt( self.R**2 + (self.w*L-(1/(self.w*C)))**2 )
        self.I_t = Vs / denom
        self.p = self.R * pow(self.I_m, 2) / 2

    def __str__(self):
        return 'Frequency: {} | Voltage: {} | AngFreq: {} | I Meas {} | I Theor {} | Power {}'.format(self.f, self.v, self.w, self.I_m, self.I_t, self.p)


def process_raw(raw, resistance):
    processed = set()
    for point in raw:
        processed.add(SSDataPoint(frequency=point[0], voltage=point[1], voltage_error=point[2], resistance=resistance))
    return processed


def tabularise(data):
    w = []
    p = []
    w_er = []
    p_er = []
    for point in data:
        w.append(point.w.nominal_value)
        p.append(point.p.nominal_value)
        w_er.append(point.w.std_dev)
        p_er.append(point.p.std_dev)
    table = pd.DataFrame(data={'w (Hz)': w, 'P (W)': p, 'w error': w_er, 'P error': p_er})
    table = table.sort_values(by=['w (Hz)'])
    print(table)
    return table


# Look over data
# Calling it Rr so it won't cause bugs if it still floating around somewhere
# as R. Messy but effective.
Rr = 1000
data = process_raw(raw_data_100, Rr)
for point in data:
    print(point)

table = tabularise(data)
w = table.get('w (Hz)')
p = table.get('P (W)')
w_er = table.get('w error')
p_er = table.get('P error')
plt.errorbar(x=w, y=p, xerr=w_er, yerr=p_er, ecolor='black', fmt='.-', capsize=2, label='Measured Current')
plt.title(label='P vs w')
plt.xlabel('w (Hz)')
plt.ylabel('P (W)')
plt.show()
