import pandas as pd

def price_treshold(price):
    std = price.std()
    median = price.median()
    gauss_min = median - 2 * std
    gauss_max = median + 2 * std
    treshold = pd.Series(price.index[(gauss_min <= price)].tolist())
    treshold = pd.Series(treshold.index[(treshold <= gauss_max)].tolist())
    
    return [-0.0001,
            treshold.quantile(.3),
            treshold.quantile(.6),
            treshold.quantile(1),
            price.max()]

def priceclass(df):
    thresholds = price_treshold(df.price)
    price_class = pd.cut(df.price,
                         bins=thresholds,
                         labels=[1, 2, 3, 4])
    print(*thresholds)

    return price_class
    
