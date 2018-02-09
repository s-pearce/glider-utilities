#
"""AllGliderTracksPlot.py  A map plot of all Endurance glider tracks

Author: Stuart Pearce
Date: 2018-01-30
Version: 0.0
"""
import datetime as dt

import numpy as np
import scipy.io
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
import pandas as pd

import sys
sys.path.append('C:/Users/spearce/code/python/glider-utilities')
from glider_utils import GSxml


# files = glob.glob('C:/Users/spearce/gliders/analysis/*gliderState.xml')



def time2ts(atime):
    return (atime - dt.datetime(1970,1,1)).total_seconds()


#GSfile = "C:\\Users\\spearce\\gliders\\analysis\\GL311-D00002-gliderState.xml"
def plot_glider_track(glider, deployment):
    GSfile = "C:\\Users\\spearce\\gliders\\analysis\\GL%d-D%05d-gliderState.xml" % (glider, deployment)
    gdeploy = GSxml(GSfile)
    timest = []
    for atime in gdeploy.timestamps:
        timest.append(time2ts(atime))
    lats = gdeploy.lats_deg
    lons = gdeploy.lons_deg
    
    ## Build Endurance map ##
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    # Setup map of Miller cylindrical
    map = Basemap(projection='mill',llcrnrlat=43,urcrnrlat=49,
                  llcrnrlon=-129,urcrnrlon=-123,resolution='h')
    # draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    # map.fillcontinents()
    # draw the edge of the map projection region (the projection limb)
    map.drawmapboundary()
    # draw lat/lon grid lines every 30 degrees.
    # 
    map.drawmeridians([-128,-127,-126,-125,-124,-123], labels=[False,False,False,True], linewidth=0.25)
    # 
    map.drawparallels([44,45,46,47,48], labels=[True,False,False,False], linewidth=0.25)

    ## Plot GPS points ##
    map.plot(lons, lats, latlon=True)
    sct = map.scatter(lons, lats, c=timest, marker='o', latlon=True)
    sct.set_edgecolors([[0., 0., 0., 0.]])
    ## Draw Map ##
    plt.title('OOI Endurance Array \nGlider %d Track %05d' % (glider, deployment)) 
    print('done')
    plt.show()
    # return sct
