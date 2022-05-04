
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

"""date_plotting_format
 Description:  date_plotting_format.py is an updated date formatter for
   the date tick marks on matplotlib plots with dates to be more readable
   than Matplotlib's auto-date formatter.  This is specifically meant to
   be a date and time formatter for scales that are hours up to years long records.
   It should be adjusted if different timescales are needed.
   
   To use, just import locator and formatter from this module and add
   them as the x (or y) axis's major locator and formatter objects.
    from date_plotting_format import locator, formatter
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    
    see the function `example_usage` below for a more in depth example
    and run it with a start and stop date string as inputs to see an
    example plot with the date tick labels.

 Author: Stuart Pearce
 Date: 2020-02-20 (last updated)
"""

locator = mdates.AutoDateLocator(interval_multiples=True)
formatter = mdates.AutoDateFormatter(locator)


class DateFormatter(object):
    """DateFormatter is simply a class that makes adjustments to the
    Matplotlib date formatter on the fly specifically in that if the day,
    month, or year advances during the record, it will add the increment
    level on a line beneath the main date/label by adding a newline in
    the format.
    This class should not be used directly though.  The locator and
    formatter object should be imported and used.
    """
    def __init__(self):
        self.last = None
        self.cursor_fmt = None
    
    def minute_format(self, x, pos=None):
        """If the autoscaling chooses this minute format, it will write
        the hour and minute as HH:MM for each tick at the main level and
        if the day increments, it will add the year, month, and day 
        below the main level as yyyy-mm-dd.
        """
        x = mdates.num2date(x)
        if pos == 0 or x.day != self.last:
            fmt = '%H:%M\n%Y-%m-%d'
        else:
            fmt = '%H:%M'
        label = x.strftime(fmt)
        self.last = x.day
        return label

    def hour_format(self, x, pos=None):
        """If the autoscaling chooses this hour format, it will write
        the hour as HH for each tick at the main level and if the day 
        increments, it will add the year, month, and day below the main
        level as yyyy-mm-dd.
        """
        x = mdates.num2date(x)
        if pos == 0 or x.day != self.last:
            fmt = '%H\n%Y-%m-%d'
        else:
            fmt = '%H'
        label = x.strftime(fmt)
        self.last = x.day
        return label

    def day_format(self, x, pos=None):
        """If the autoscaling chooses this day format, it will write
        the day as dd for each tick at the main level and if the month
        increments, it will add the year and month below the main
        level as yyyy-mm.
        """
        x = mdates.num2date(x)
        if pos == 0 or x.month != self.last:
            fmt = '%d\n%Y-%m'
        else:
            fmt = '%d'
        label = x.strftime(fmt)
        self.last = x.month
        return label

    def month_format(self, x, pos=None):
        """If the autoscaling chooses this month format, it will write
        the month as mm for each tick at the main level and if the year
        increments, it will add the year below the main level as yyyy.
        """    
        x = mdates.num2date(x)
        if pos == 0 or x.year != self.last:
            fmt = '%m\n%Y'
        else:
            fmt = '%m'
        label = x.strftime(fmt)
        self.last = x.year
        return label


def set_date_formatter(ax=None):
# instantiate the DateFormatter class here to pass to the matplotlib
# formatter object where the scales change for the format types.
    locator = mdates.AutoDateLocator(interval_multiples=True)
    formatter = mdates.AutoDateFormatter(locator)
    tf = DateFormatter()

    formatter.scaled[1./(24.*60.)] = FuncFormatter(tf.minute_format)
    formatter.scaled[1./24.] = FuncFormatter(tf.hour_format)
    formatter.scaled[1.0] = FuncFormatter(tf.day_format)
    formatter.scaled[30] = FuncFormatter(tf.month_format)
    if ax:
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
    return locator, formatter


def example_usage(start, end, num_pts=1000):
    """
    Example plot using the date_plotting_format formatter
    
    Creates a plot with random data between two given dates that 
    demonstrates how the date formatter in this module appears in a 
    figure with dates and times on the xlabel for timeseries data.
    
    Parameters
    ----------
    start, end : datetime str
        The start and end date and time as a string of the format 
        'yyyy-mm-dd HH:MM'.
    num_pts : optional int
        The number of points of random data points to plot at equal
        intervals between `date1` and `date2`
    
    """
    # don't need these imports at the module level
    import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    
    date1 = datetime.datetime.strptime(start,'%Y-%m-%d %H:%M')
    date2 = datetime.datetime.strptime(end,'%Y-%m-%d %H:%M')
    
    # get a time interval for `num_pts` worth of random data
    delta = (date2 - date1)/(num_pts-1)

    dates = mdates.drange(date1, date2, delta)
    yvals = np.random.rand(len(dates))  # make up some random y values
    
    ax = plt.subplot()
    ax.plot(dates, yvals, 'r.')

    # this step uses the locator and formatter objects created in this
    # module
    #ax.xaxis.set_major_locator(locator)
    #ax.xaxis.set_major_formatter(formatter)
    locator, formatter = set_date_formatter(ax)

    # this step sets the format of the mouse-hover display in the corner
    # of the figure window.  This is meant to have a similar format as 
    # the xaxis format, but normally I would set this differently using
    # mdates.DateFormatter("%Y-%m-%d %H:%M")
    cursor_fmt = mdates.AutoDateFormatter(locator)
    # _, cursor_fmt = set_date_formatter()
    # cursor_fmt = formatter
    print(cursor_fmt)
    ax.format_xdata = cursor_fmt
    plt.show()

def example_concise(start, end, num_pts=1000):
    """
    Example plot using the date_plotting_format formatter
    
    Creates a plot with random data between two given dates that 
    demonstrates how the date formatter in this module appears in a 
    figure with dates and times on the xlabel for timeseries data.
    
    Parameters
    ----------
    start, end : datetime str
        The start and end date and time as a string of the format 
        'yyyy-mm-dd HH:MM'.
    num_pts : optional int
        The number of points of random data points to plot at equal
        intervals between `date1` and `date2`
    
    """
    # don't need these imports at the module level
    import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    
    date1 = datetime.datetime.strptime(start,'%Y-%m-%d %H:%M')
    date2 = datetime.datetime.strptime(end,'%Y-%m-%d %H:%M')
    
    # get a time interval for `num_pts` worth of random data
    delta = (date2 - date1)/(num_pts-1)

    dates = mdates.drange(date1, date2, delta)
    yvals = np.random.rand(len(dates))  # make up some random y values
    
    fig, axs = plt.subplots(2, 1, figsize=(10, 9))
    ax1 = axs[0]
    ax1.plot(dates, yvals, 'r.')

    # this step uses the locator and formatter objects created in this
    # module
    locator = mdates.AutoDateLocator(interval_multiples=True)
    ax1.xaxis.set_major_locator(locator)
    ax1.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    ax1.set_title('Example of Concise Date Formatter')
    
    # this step sets the format of the mouse-hover display in the lower
    # left corner of the figure window
    cursor_fmt = mdates.AutoDateFormatter(locator)
    ax1.format_xdata = cursor_fmt
    
    # Second figure, using my formatter
    ax2 = axs[1]
    ax2.plot(dates, yvals, 'r.')

    # this step uses the locator and formatter objects created in this
    # module
    mylocator, _ = set_date_formatter(ax2)
#    ax2.xaxis.set_major_locator(locator)
#    ax2.xaxis.set_major_formatter(formatter)

    ax2.set_title("Example of This Module's Date Formatter")
    
    # this step sets the format of the mouse-hover display in the lower
    # left corner of the figure window
    cursor_fmt = mdates.AutoDateFormatter(mylocator)
    ax2.format_xdata = cursor_fmt
    
    # add in later
    #ax2.format_ydata = mdates.DateFormatter('%Y-%m-%d %H:%M')
    plt.show()