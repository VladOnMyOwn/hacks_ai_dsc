import pandas as pd
from scipy.sparse import csr_matrix
from scipy.stats import logistic
from sklearn.preprocessing import MultiLabelBinarizer


class Item2ItemRS():


    def __init__(self):
        self.data = pd.DataFrame()
        self.freq = pd.DataFrame()
        self.time_freq = pd.DataFrame()
        self.area_freq = pd.DataFrame()
        self.most_popular = None


    def fill_freq(self, freq: pd.DataFrame):
        self.freq = freq


    def fill_time_freq(self, freq: pd.DataFrame):
        self.time_freq = freq


    def fill_area_freq(self, freq: pd.DataFrame):
        self.area_freq = freq


    def __get_i2i_matrix(self) -> pd.DataFrame:

        item_lists = self.data.groupby(['receipt_id']).item_id.apply(list).tolist()

        mlb = MultiLabelBinarizer()
        item_matrix = mlb.fit_transform(item_lists)

        item_matrix_csr = csr_matrix(item_matrix)
        item_to_item_matrix = item_matrix_csr.T.dot(item_matrix_csr)

        item_to_item_matrix.setdiag(0)
        item_to_item_df = pd.DataFrame(item_to_item_matrix.toarray(), columns=mlb.classes_, index=mlb.classes_)

        return item_to_item_df


    class Seasonality:
        periods = ['season', 'month', 'dayofweek', 'hour']


    seas_period = Seasonality.periods[1]


    def __get_season_freq_matrix(self, date_col: str, period: str = seas_period) -> pd.DataFrame:

        data_to_agg = self.data.copy()
        data_to_agg[date_col] = pd.to_datetime(data_to_agg[date_col])

        seasonality = self.Seasonality.periods
        if period == seasonality[0]:
            data_to_agg[seasonality[0]] = data_to_agg[date_col].dt.month % 12 // 3 + 1
        elif period == seasonality[1]:
            data_to_agg[seasonality[1]] = data_to_agg[date_col].dt.month
        elif period == seasonality[2]:
            data_to_agg[seasonality[2]] = data_to_agg[date_col].dt.dayofweek
        elif period == seasonality[3]:
            data_to_agg[seasonality[3]] = data_to_agg[date_col].dt.hour

        quantities = pd.crosstab(index=data_to_agg[period], columns=data_to_agg.item_id,
                                 values=data_to_agg.quantity, aggfunc='sum').fillna(0).astype(int).reset_index()
        quantities.columns.name = ''
        quantities.set_index(period, inplace=True)
        quantities = quantities.div(quantities.max(axis=1), axis=0)

        return quantities


    def __get_area_freq_matrix(self) -> pd.DataFrame:

        data_to_agg = self.data.copy()

        device_quantities = pd.crosstab(index=data_to_agg.device_id, columns=data_to_agg.item_id,
                                        values=data_to_agg.quantity, aggfunc='sum').fillna(0).astype(int).reset_index()
        device_quantities.columns.name = ''
        device_quantities.set_index('device_id', inplace=True)
        device_quantities = device_quantities.div(device_quantities.max(axis=1), axis=0)

        return device_quantities


    def __get_most_popular(self, data: pd.DataFrame):
        return data.groupby(['item_id']).quantity.sum().sort_values(ascending=False).index[0]


    def fit(self, data: pd.DataFrame):
        self.data = data
        self.freq = self.__get_i2i_matrix()
        self.time_freq = self.__get_season_freq_matrix('local_date', self.seas_period)
        self.area_freq = self.__get_area_freq_matrix()
        self.most_popular = self.__get_most_popular(data)


    def update(self):
        pass


    def predict(self, sample: pd.DataFrame) -> tuple:

        prep_data = sample
        basket = set(prep_data.item_id.values[0])
        if self.seas_period == self.Seasonality.periods[0]:
            sample_time_part = pd.to_datetime(prep_data.local_date.values[0]).month % 12 // 3 + 1
        elif self.seas_period == self.Seasonality.periods[1]:
            sample_time_part = pd.to_datetime(prep_data.local_date.values[0]).month
        elif self.seas_period == self.Seasonality.periods[2]:
            sample_time_part = pd.to_datetime(prep_data.local_date.values[0]).dayofweek
        else:
            sample_time_part = pd.to_datetime(prep_data.local_date.values[0]).hour
        # device = prep_data.device_id.values[0]

        try:
            basket = basket.intersection(self.freq.index.values)
        except AttributeError:
            print('Empty basket!')
            return self.most_popular, None

        if len(basket) == 0:
            print('No such product!')
            return self.most_popular, None

        res = pd.DataFrame(index=list(self.freq.columns))
        res['numerator'] = self.freq[list(basket)].sum(axis=1)
        res['denominator'] = self.freq[list(set(self.freq.keys()).difference(basket))].sum(axis=1)
        res['proba'] = res.numerator / res.T[list(basket)].T.denominator.sum()
        res['time_freq'] = self.time_freq[self.time_freq.index == int(sample_time_part)].T.squeeze()
        # res['area_freq'] = self.area_freq[self.area_freq.index == int(device)].T.squeeze()
        res['weighted_proba'] =  res.proba * logistic.cdf(res.time_freq)
        res['proba_calibr'] = logistic.cdf(res.weighted_proba)
        res = res.sort_values(by='proba_calibr', ascending=False)
        best_offer = res.loc[~res.index.isin(basket)].head(1).index[0]

        return best_offer, list(zip(res.index, res.proba_calibr))
