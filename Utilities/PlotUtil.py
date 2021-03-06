import matplotlib.pyplot as plt
import datetime
import numpy as np
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
from typing import Dict, List, Union

class DateConstant:
    """
    First day of each month, count as day of year
    """
    Jan = 1
    Feb = 32
    Mar = 60
    Apr = 91
    May = 121
    Jun = 152
    Jul = 182
    Aug = 213
    Sep = 244
    Oct = 274
    Nov = 305
    Dec = 335


# class Figure:
#     def plot(self):
#         data1 = np.random.normal(1, 0.2, 365)
#         data2 = np.random.normal(3, 0.1, 365)
#         date = np.arange(1, 366)
#         plt.plot(date, data1)
#         plt.plot(date, data2)
#         ax = plt.gca()
#         ax.set_xlim(1, 366)
#         ax.set_xticks([DateConstant.Jan, DateConstant.Feb, DateConstant.Mar, DateConstant.Apr,
#                        DateConstant.May, DateConstant.Jun, DateConstant.Jul, DateConstant.Aug,
#                        DateConstant.Sep, DateConstant.Oct, DateConstant.Nov, DateConstant.Dec])
#         ax.set_xticklabels(['01/01', '02/01', '03/01', '04/01', '05/01', '06/01',
#                             '07/01', '08/01', '09/01', '10/01', '11/01', '12/01'], rotation=45)
#         plt.show()


class PlotUtil:
    def __init__(self):

        # plt.rcParams['font.sans-serif'] = ['STKaiti']
        plt.rcParams.update({'font.size': 11})
        self.c1 = "#CC0000"
        self.c2 = "#8C8C8C"
        self.c3 = "#FF6464"
        self.c4 = "#1E1E1E"
        self.c5 = "#FFC8C8"
        self.c6 = "#5A5A5A"
        self.c7 = "#FF9664"
        self.c8 = "#B4B4B4"
        self.c9 = "#FFD27D"
        self.c10 = "#918CD7"

        self.dash = [7, 2, 3, 2]

        self.l1 = "-"
        self.l2 = "-"
        self.l3 = "--"
        self.l4 = "--"
        self.l5 = "-."
        self.l6 = self.l3
        self.l7 = self.l1
        self.l8 = self.l3
        self.l9 = self.l1
        self.l10 = self.l2

        self.date_fmt = "%m/%y"

        self.colors = [self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, self.c9, self.c10]
        self.lines = [self.l1, self.l2, self.l3, self.l4, self.l5, self.l6, self.l7, self.l8, self.l9, self.l10]

    def set_frame(self, axarrs):
        for axarr in axarrs:
            axarr.spines['right'].set_visible(False)
            axarr.spines['top'].set_visible(False)
            axarr.yaxis.set_ticks_position('left')
            axarr.xaxis.set_ticks_position('bottom')
        return axarrs

    def plot_line(self, ax, count, x, y, lgd='', x_label='', y_label=''):
        c = self.colors[count % 10]
        l = self.lines[count % 10]
        if lgd == '':
            if count == 3:
                tmp, = ax.plot(x, y, color=c, linestyle=l, linewidth=2)
                tmp.set_dashes(self.dash)
            elif count == 0:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2)
            else:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2)
        else:
            if count == 3:
                tmp, = ax.plot(x, y, color=c, linestyle=l, linewidth=2, label=lgd)
                tmp.set_dashes(self.dash)
            elif count == 0:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2, label=lgd)
            else:
                ax.plot(x, y, color=c, linestyle=l, linewidth=2, label=lgd)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        self.set_frame([ax])

    def plot_scatter(self, ax, count, x, y, lgd='', x_label='', y_label=''):
        c = self.colors[count]
        if lgd == '':
            if count == 3:
                tmp, = ax.scatter(x, y, color=c)
                tmp.set_dashes(self.dash)
            elif count == 0:
                ax.scatter(x, y, color=c)
            else:
                ax.scatter(x, y, color=c)
        else:
            if count == 3:
                tmp, = ax.scatter(x, y, color=c, label=lgd)
                tmp.set_dashes(self.dash)
            elif count == 0:
                ax.scatter(x, y, color=c, label=lgd)
            else:
                ax.scatter(x, y, color=c,  label=lgd)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        self.set_frame([ax])


    def plot_line_chart(self, x, Y, legends=None, x_label='', y_label=''):
        f, ax = plt.subplots()
        for idx, y in enumerate(Y):
            if legends is None:
                self.plot_line(ax, idx, x, y)
            else:
                lgd = legends[idx]
                self.plot_line(ax, idx, x, y, lgd)
        ax.legend(frameon=False)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        self.set_frame([ax])
        return f

    def plot_scatter_chart(self, x, Y, legends, x_label='', y_label=''):
        f, ax = plt.subplots()
        for idx, y in enumerate(Y):
            lgd = legends[idx]
            self.plot_scatter(ax, idx, x, y, lgd)
        ax.legend(frameon=False)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        self.set_frame([ax])
        return f

    # 将df的数据按年分割画图
    def plot_yearly_line_chart(self,df:pd.DataFrame,col_y,col_date):
        f, ax = plt.subplots()
        df['y'] = df[col_date].apply(lambda x:x.strftime("%Y"))
        df['day_of_year'] = df[col_date].apply(lambda x:x.timetuple().tm_yday)
        years = sorted(df['y'].unique(),reverse=True)
        count = 0
        for y in years:
            df_y = df[df['y']==y].copy()
            self.plot_line(ax,count,list(df_y['day_of_year']),list(df_y[col_y]),col_y+' : ' + y)
            count += 1
        ax.legend(frameon=False,loc='upper center',ncol=int(count/2))
        ax.set_xlim(1, 366)
        ax.set_xticks([DateConstant.Jan, DateConstant.Feb, DateConstant.Mar, DateConstant.Apr,
                       DateConstant.May, DateConstant.Jun, DateConstant.Jul, DateConstant.Aug,
                       DateConstant.Sep, DateConstant.Oct, DateConstant.Nov, DateConstant.Dec])
        ax.set_xticklabels(['01/01', '02/01', '03/01', '04/01', '05/01', '06/01',
                            '07/01', '08/01', '09/01', '10/01', '11/01', '12/01'], rotation=90)
        self.set_frame([ax])
        return f



    def example_date_tick_labels(self):
        """
        ================
        Date tick labels
        ================

        Show how to make date plots in matplotlib using date tick locators and
        formatters.  See major_minor_demo1.py for more information on
        controlling major and minor ticks

        All matplotlib date plotting is done by converting date instances into
        days since the 0001-01-01 UTC.  The conversion, tick locating and
        formatting is done behind the scenes so this is most transparent to
        you.  The dates module provides several converter functions date2num
        and num2date

        """

        years = mdates.YearLocator()  # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        # Load a numpy record array from yahoo csv data with fields date, open, close,
        # volume, adj_close from the mpl-data/example directory. The record array
        # stores the date as an np.datetime64 with a day unit ('D') in the date column.
        with cbook.get_sample_data('goog.npz') as datafile:
            r = np.load(datafile)['price_data'].view(np.recarray)
        # Matplotlib works better with datetime.datetime than np.datetime64, but the
        # latter is more portable.
        date = r.date.astype('O')

        fig, ax = plt.subplots()
        ax.plot(date, r.adj_close)

        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        datemin = datetime.date(date.min().year, 1, 1)
        datemax = datetime.date(date.max().year + 1, 1, 1)
        ax.set_xlim(datemin, datemax)

        # format the coords message box
        def price(x):
            return '$%1.2f' % x

        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = price
        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        return fig
