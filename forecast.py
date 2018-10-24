import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

from datetime import datetime
from sklearn.linear_model import LinearRegression
from constants import DATA_PATH, PIC_PATH

import warnings

warnings.filterwarnings("ignore")
sns.set()


def code_target(data, cat_feature, real_feature, agg='mean'):
    return dict(data.groupby(cat_feature)[real_feature].agg(agg))


def make_future_dataset(data):
    start = data.index.max()
    end = datetime(start.year, start.month, start.day, 22, 30)

    dates = pd.date_range(start=start, end=end, freq='min')
    dates = dates[dates > start]

    dates = pd.DataFrame(dates)
    dates.columns = ['date']
    dates.set_index('date', inplace=True)

    return dates


def prepare_date(data, idx, lag_start=60, lag_end=360):
    data['hour'] = data.index.hour
    data['minute'] = data.index.minute

    funcs = ['mean', 'std']
    for func in funcs:
        data['hour_{}'.format(func)] = list(map(code_target(data[:idx], 'hour', 'pool_count', func).get, data.hour))
        data['min_{}'.format(func)] = list(map(code_target(data[:idx], 'minute', 'pool_count', func).get, data.minute))
    data.drop(['hour', 'minute'], axis=1, inplace=True)

    for i in range(lag_start, lag_end + 1):
        data["lag_{}".format(i)] = data.pool_count.shift(i)

    for col in data.columns:
        if col.startswith('lag_'):
            data[col].fillna(data[col].mean(), inplace=True)

    x_train = data.iloc[:idx].drop(['pool_count'], axis=1)
    y_train = data.iloc[:idx]['pool_count']
    x_test = data.iloc[idx:].drop(['pool_count'], axis=1)

    return x_train, y_train, x_test


def train_predict(x_train, y_train, x_test):
    lr = LinearRegression()
    lr.fit(x_train, y_train)
    prediction = lr.predict(x_test)
    return prediction


def make_prediction_pic(data, data_future, pred_future):
    morning = '{}'.format(datetime.now().strftime('%Y-%m-%d')) + ' 07:00:00'

    hours = mdates.HourLocator()
    hour_fmt = mdates.DateFormatter('%H:%M')

    date_min = data[morning:].index.min()
    date_max = data_future.index.max()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(data[morning:], 'b', label='текущее', linewidth=3.0)
    ax.plot(pred_future, 'r', label='прогноз', linewidth=3.0)

    ax.legend(loc='upper left')
    ax.axvspan(data_future.index.min(), date_max, facecolor='r', alpha=0.25)
    ax.set_ylabel('Посетители', fontsize=18)
    ax.set_xlabel('Время', fontsize=18)
    ax.set_title('Количество посетителей в бассейне {}'.format(datetime.now().strftime("%d.%m.%Y")), fontsize=18)

    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(hour_fmt)
    ax.set_xlim(date_min, date_max)
    fig.autofmt_xdate()

    ax.grid (True)
    plt.savefig(PIC_PATH + 'prediction.png')


def make_forecast():
    main()


def main():
    data = pd.read_csv(DATA_PATH, usecols=['pool_count', 'date'], index_col=['date'], parse_dates=['date'])
    data_future = make_future_dataset(data)

    lag_start = len(data_future)
    lag_end = lag_start + 600
    idx = len(data)

    data_temp = pd.concat([data, data_future])

    x_train, y_train, x_test = prepare_date(data_temp, idx, lag_start, lag_end)
    pred = train_predict(x_train, y_train, x_test)

    pred_future = pd.DataFrame(pred)
    pred_future.columns = ['pool_count']
    pred_future.index = data_future.index

    make_prediction_pic(data, data_future, pred_future)


if __name__ == '__main__':
    main()
