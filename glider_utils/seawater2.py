import pygsw.vectors as gsw

"""Seawater module for calculating density and salinity from
conductivity, temperature, pressure, latitude, and longitude.
Functions work for gliders and standard CTDs.

Depends on the pygsw package which depends on the TEOS-10 C
libraries to be installed as libraries.
-Stuart Pearce
"""

def rho_sp_glider(cond, temp, pres, lat=46.0, lon=-124.5):
    """density and salinity from glider CTD.
    
    Returns in-situ density and practical salinity from 
    conductivity, temperature, pressure, latitude, and 
    longitude as reported from a Slocum glider with a 
    Seabird pumped glider CTD.
    
    Usage:
        Rho, SP = rho_sp_glider(cond, temp, pres, lat, lon)
        
        where
        
        Rho = in-situ density, [kg/m^3]
        SP = practical salinity, [pss]
        cond = conductivity, [S/m]
        temp = temperature, [deg C]
        pres = pressure, [bar]
        lat = latitude, decimal degrees +N
        lon = longitude, decimal degrees +E
    """
    cond = cond * 10.  # convert from glider S/m to mS/cm
    pres = pres * 10.  # convert from glider bar to dbar
    Rho, SP = rho_sp(cond, temp, pres, lat, lon)
    return Rho, SP


def rho_sp(cond, temp, pres, lat=46.0, lon=-124.5):
    """density and salinity from a CTD.
    
    Returns in-situ density and practical salinity from 
    conductivity, temperature, pressure, latitude, and 
    longitude as reported from any standard CTD.
    
    Usage:
        Rho, SP = rho_sp(cond, temp, pres, lat, lon)
        
        where
        
        Rho = in-situ density, [kg/m^3]
        SP = practical salinity, [pss]
        cond = conductivity, [mS/cm]
        temp = temperature, [deg C]
        pres = pressure, [dbar]
        lat = latitude, decimal degrees +N
        lon = longitude, decimal degrees +E
    """
    SP = gsw.sp_from_c(cond, temp, pres)
    SA = gsw.sa_from_sp(SP, pres, lon, lat)
    CT = gsw.ct_from_t(SA, temp, pres)
    Rho = gsw.rho(SA, CT, pres)
    return Rho, SP


def rho_from_sp(SP, temp, pres, lat=46.0, lon=-124.5):
    """density from salinity from a CTD.
    
    Returns in-situ density and practical salinity from 
    conductivity, temperature, pressure, latitude, and 
    longitude as reported from any standard CTD.
    
    Usage:
        Rho = rho_from_sp(SP, temp, pres, lat, lon)
        
        where
        
        Rho = in-situ density, [kg/m^3], use pres=0.0 for potential density
        SP = practical salinity, [pss]
        temp = temperature, [deg C]
        pres = pressure, [dbar]
        lat = latitude, decimal degrees +N
        lon = longitude, decimal degrees +E
    """

    SA = gsw.sa_from_sp(SP, pres, lon, lat)
    CT = gsw.ct_from_t(SA, temp, pres)
    Rho = gsw.rho(SA, CT, pres)
    return Rho