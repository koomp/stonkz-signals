import numpy as np

def tenkan_sen(data_high, data_low, period = 9, fill_empty = True):
    tenkan = []
    if fill_empty:
        tenkan = [None] * period
        tenkan = tenkan + [(max(data_high[i-period:i]) + min(data_low[i-period:i])) / 2 for i in range(period,len(data_high))]
    else:
        tenkan = [(max(data_high[i-period:i]) + min(data_low[i-period:i])) / 2 for i in range(period,len(data_high))]
    
    return np.array(tenkan)

def kijun_sen(data_high, data_low, fill_empty = True, period=26):
    return tenkan_sen(data_high, data_low, period, fill_empty)

def span_a(data_high, data_low, period = 26, tenkan_period = 9, kijun_period = 26):
    tenkan = tenkan_sen(data_high, data_low, period = tenkan_period, fill_empty = False)
    kijun = kijun_sen(data_high, data_low, period = kijun_period, fill_empty = False)
    a = (tenkan[kijun_period - tenkan_period:] + kijun) / 2
    # shift
    a = np.insert(a, 0, [None] * (period + kijun_period))
    return a

def span_b(data_high, data_low, period = 52):
    b = tenkan_sen(data_high, data_low, period = period, fill_empty=False)
    # shift
    shift = 26
    b = np.insert(b, 0, [None]*(period + shift))
    return b

def buy_signal(data_high, data_low, data_close):
    tenkan = tenkan_sen(data_high, data_low)
    kijun = kijun_sen(data_high, data_low)
    a = span_a(data_high, data_low)
    b = span_b(data_high, data_low)
    shift = -26
    chikou = data_close[shift]
    # tenkan < kijun && span_a > span_b && tenknan < chikou && tenkan > span_a
    # print("span b {}".format(b))
    # print("Values: tenkan {} kijun {} span_a {}, span_b {}, chikou {}".format(tenkan[-1], kijun[-1], a[shift], b[shift], chikou))
    signal = tenkan[-1] < kijun[-1] and a[shift] > b[shift] and tenkan[-1] < chikou and tenkan[-1] > a[shift]
    return signal
