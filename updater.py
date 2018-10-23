import time
import csv

from crawl import get_visitors
from datetime import datetime
from constants import UPD_DELAY, DATA_PATH

import warnings
warnings.filterwarnings("ignore")


def write_data(path, data):
    with open(path, 'a', newline='\n') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def get_data(pool_visitors, curr_t):
    if pool_visitors is None:
        return [0, 0, 0, str(curr_t)]
    return [*pool_visitors, str(curr_t)]


def main():
    while True:
        pool_visitors, curr_t = get_visitors(), datetime.now()
        data = get_data(pool_visitors, curr_t)

        write_data(DATA_PATH, data)
        print('Done! Added line {} into file'.format(data))

        time.sleep(UPD_DELAY)


if __name__ == '__main__':
    main()
