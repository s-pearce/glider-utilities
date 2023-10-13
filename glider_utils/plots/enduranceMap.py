#Endurance map
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np


def ce_map(
    urlat=49, urlon=-123, lllat=43, lllon=-129,
    meridians=[-128,-127,-126,-125,-124,-123],
    parallels=[44,45,46,47,48],):

    ## Build Endurance map ##
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    # Setup map of Miller cylindrical
    cem = Basemap(
        projection='mill',
        llcrnrlat=lllat,
        urcrnrlat=urlat,
        llcrnrlon=lllon,
        urcrnrlon=urlon,
        resolution='h')
    # draw coastlines, country boundaries, fill continents.
    cem.drawcoastlines(linewidth=0.25)
    cem.drawcountries(linewidth=0.25)
    cem.fillcontinents()
    # draw the edge of the map projection region (the projection limb)
    cem.drawmapboundary()

    if not meridians:
        meridians = np.arange(lllon, urlon, 6)
    cem.drawmeridians(
        meridians,
        labels=[False,False,False,True], linewidth=0.25)
    # 
    if not parallels:
        parallels = np.arange(lllat, urlat, 6)
    cem.drawparallels(
        parallels, 
        labels=[True,False,False,False], linewidth=0.25)

    # make bathymetry contours
    mat = scipy.io.loadmat('ETOPO1.mat')
    lon = mat['ETOPO1_Lon']
    lat = mat['ETOPO1_Lat']
    depth = mat['ETOPO1']
    lon, lat = np.meshgrid(lon,lat)

    # create levels for contouring
    levels = [25,50,75,100,200,500,800,1000,2000,3000,4000]
    cs = cem.contourf(lon,lat,depth,levels,cmap=cm.Blues,linewidth=0.5,latlon=True)
    cs = cem.contour(lon,lat,depth,levels, linewidth=0.001, colors='k', latlon=True)
    plt.clabel(cs, levels, inline_spacing=10, fontsize=10, colors='k',fmt='%d')
    
    return cem



