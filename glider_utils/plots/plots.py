# Glider Plotter module: gliderplots.py

import matplotlib.pyplot as pl
import matplotlib.dates as mdates


mints = mdates.MinuteLocator(interval=30)
days = mdates.DayLocator()
mnths = mdates.MonthLocator()
mintsFmt = mdates.DateFormatter('%H:%M')
daysMnFmt = mdates.DateFormatter('%d')
daysMjFmt = mdates.DateFormatter('\n%d')
mnthFmt = mdates.DateFormatter('\n%m')

def set_xticklabels_empty(ax):
    n_majorlabels = len(ax.get_xmajorticklabels())
    empty_majorlabels = [''] * n_majorlabels
    n_minorlabels = len(ax.get_xminorticklabels())
    empty_minorlabels = [''] * n_minorlabels
    ax.set_xticklabels(empty_majorlabels)
    ax.set_xticklabels(empty_minorlabels, minor=True)

def autoTSdateFormat(ax, major='months', minor='days', xlim=None):
    if xlim:
        ax.set_xlim(xlim)
    else:
        xlim = ax.get_xlim()
    
    # assuming a pandas type datetime index series
    diff = xlim[-1] - xlim[0]
    
    if diff < 86400:
        pass
    if major=='months':
        ax.xaxis.set_major_locator(mnths)
        ax.xaxis.set_major_formatter(mnthFmt)
    elif major=='days':
        ax.xaxis.set_major_locator(days)
        ax.xaxis.set_major_formatter(daysMjFmt)
        
    if minor=="days":
        ax.xaxis.set_minor_locator(days)
        ax.xaxis.set_minor_formatter(daysMnFmt)
    elif minor=="minutes":
        ax.xaxis.set_minor_locator(mints)
        ax.xaxis.set_minor_formatter(mintFmt)
    
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    
def setTSdateFormat(ax, xlim=None):
    if xlim:
        ax.set_xlim(xlim)

    ax.xaxis.set_major_locator(mnths)
    ax.xaxis.set_major_formatter(mnthFmt)
  
    ax.xaxis.set_minor_locator(days)
    ax.xaxis.set_minor_formatter(daysMnFmt)

    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    

def profileScatter(TS, Z, ClrVar, **kwargs):
    if 'ax' in kwargs:
        ax = kwargs.pop('ax')
    else:
        ax = pl.gca()
    sc = ax.scatter(TS, Z, c=ClrVar, **kwargs)
    ax.invert_yaxis()

    setTSdateFormat(ax, xlim=(TS.min(), TS.max()))
    cb = pl.colorbar(sc, ax=ax)
    return cb
    
def TSplot(*args, **kwargs):
    """TSplot:  basic Time Series Plot
    Time Series plot using a Pandas DateTimeIndex series as the
    X axis scale and nicely formatting of the dates/times.
    """
    if 'ax' in kwargs:
        ax = kwargs.pop('ax')
    else:
        ax = pl.gca()
    ax.plot(*args, **kwargs)
    setTSdateFormat(ax)


## Specific plots
def tempProfPlot(TS, Z, Temp, **kwargs):

    cb = profileScatter(TS, Z, Temp, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Temperature, [$^\circ$ C]')

def condProfPlot(TS, Z, Cond, **kwargs):

    cb = profileScatter(TS, Z, Cond, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Conductivity, [S/m]')


def saltProfPlot(TS, Z, Salinity, **kwargs):

    cb = profileScatter(TS, Z, Salinity, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('Salinity, [psu]')


def densityProfPlot(TS, Z, Density, **kwargs):
    #find out how to use **kwargs for title

    if 'vmin' in kwargs:
        vmin = kwargs['vmin']
    else:
        vmin = 19.0
    cb = profileScatter(TS, Z, Density, ax=ax, vmin=19.0, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('Density, [kg/m^3]')

def oxyProfPlot(TS, Z, OXY, **kwargs):

    cb = profileScatter(TS, Z, OXY, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('Oxygen, [umol/L]')

def chlorProfPlot(TS, Z, Chlor, **kwargs):

    cb = profileScatter(TS, Z, Chlor, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('Chlorophyll, [ug/L]')
    
def cdomProfPlot(TS, Z, CDOM, **kwargs):

    cb = profileScatter(TS, Z, CDOM, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('CDOM, [ppb]')
    
def bbProfPlot(TS, Z, BB, **kwargs):

    cb = profileScatter(TS, Z, BB, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('Backscatter, [no dim]')
    
def parProfPlot(TS, Z, PAR, **kwargs):

    cb = profileScatter(TS, Z, PAR, **kwargs)
    pl.ylabel('Pressure, [dbar]')
    cb.set_label('PAR, [uE/m^2sec]')

    
## Glider Health Plots ##
# Pitch
def pitchPlot(TS, Pitch, **kwargs):

    TSplot(TS, Pitch, 'r.', **kwargs)
    #ax.set_title('Glider Dive & Climb Pitch Angles')
    pl.ylabel('Pitch, [degrees]')

# Roll
def rollPlot(TS, Roll, **kwargs):

    TSplot(TS, Roll, 'g.', **kwargs)
    #ax.set_title('Glider Roll Angle')
    pl.ylabel('Roll, [degrees]')

def headingPlot(TS, Heading, **kwargs):

    TSplot(TS, Heading, 'b.', **kwargs)
    #ax.set_title('Glider Roll Angle')
    pl.ylabel('Roll, [degrees]')
    
def finPlot(TS, Fin, **kwargs):

    TSplot(TS, Fin, 'y.', **kwargs)
    #ax.set_title('Glider Roll Angle')
    pl.ylabel('Roll, [degrees]')

def batteryPlot(TS, Volts, **kwargs):

    TSplot(TS, Volts, 'k.', **kwargs)
    #ax.set_title('Glider Roll Angle')
    pl.ylabel('Roll, [degrees]')
# Battery Voltage
# Altitude / Bottom depth
# Vacuum