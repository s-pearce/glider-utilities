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
    

def profileScatter(TS, Z, ClrVar, ax=None, **kwargs):
    if not ax:
        ax = pl.gca()
    sc = ax.scatter(TS, Z, c=ClrVar, **kwargs)
    ax.invert_yaxis()

    setTSdateFormat(ax, xlim=(TS.min(), TS.max()))
    cb = pl.colorbar(sc, ax=ax)
    return cb
    
def TSplot(*args, ax=None, **kwargs):
    """TSplot:  basic Time Series Plot
    Time Series plot using a Pandas DateTimeIndex series as the
    X axis scale and nicely formatting of the dates/times.
    """
    if not ax:
        ax = pl.gca()
    ax.plot(*args, **kwargs)
    setTSdateFormat(ax)

def tempProfPlot(TS, Z, Temp, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, Temp, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Temperature, [$^\circ$ C]')

def condProfPlot(TS, Z, Cond, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, Cond, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Conductivity, [S/m]')


def saltProfPlot(TS, Z, Salinity, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, Salinity, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Salinity, [psu]')


def densityProfPlot(TS, Z, Density, ax=None, **kwargs):
    #find out how to use **kwargs for title
    if not ax:
        fig, ax = pl.subplots()

    if 'vmin' in **kwargs:
        vmin = **kwargs['vmin']
    else:
        vmin = 19.0
    cb = profileScatter(TS, Z, Density, ax=ax, vmin=19.0, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Density, [kg/m^3]')


def chlorProfPlot(TS, Z, Chlor, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, Chlor, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Chlorophyll, [ug/L]')
    
def cdomProfPlot(TS, Z, CDOM, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, CDOM, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('CDOM, [ppb]')
    
def bbProfPlot(TS, Z, BB, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, BB, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('Backscatter, [no dim]')
    
def parProfPlot(TS, Z, PAR, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    cb = profileScatter(TS, Z, PAR, ax=ax, **kwargs)
    ax.set_ylabel('Pressure, [dbar]')
    cb.set_label('PAR, [uE/m^2sec]')

    
## Glider Health Plots ##
# Pitch
def pitchPlot(TS, Pitch, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    TSplot(TS, Pitch, 'r.', ax=ax, **kwargs)
    #ax.set_title('Glider Dive & Climb Pitch Angles')
    ax.set_ylabel('Pitch, [degrees]')

# Roll
def rollPlot(TS, Roll, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    TSplot(TS, Roll, 'g.', ax=ax, **kwargs)
    #ax.set_title('Glider Roll Angle')
    ax.set_ylabel('Roll, [degrees]')

def headingPlot(TS, Heading, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    TSplot(TS, Heading, 'b.', ax=ax, **kwargs)
    #ax.set_title('Glider Roll Angle')
    ax.set_ylabel('Roll, [degrees]')
    
def finPlot(TS, Fin, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    TSplot(TS, Fin, 'y.', ax=ax, **kwargs)
    #ax.set_title('Glider Roll Angle')
    ax.set_ylabel('Roll, [degrees]')

def batteryPlot(TS, Volts, ax=None, **kwargs):
    if not ax:
        fig, ax = pl.subplots()
    TSplot(TS, Volts, 'k.', ax=ax, **kwargs)
    #ax.set_title('Glider Roll Angle')
    ax.set_ylabel('Roll, [degrees]')
# Battery Voltage
# Altitude / Bottom depth
# Vacuum