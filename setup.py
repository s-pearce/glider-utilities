from distutils.core import setup
from setuptools import find_packages

packages=find_packages()

setup(
    name='glider-utilities',
    version='1.2',
    description='Suite of Slocum Glider Python Utilities',
    license='LICENSE',
    author='Stuart Pearce',
    author_email='spearce@ceoas.oregonstate.edu',
    keywords=['oceanography', 'Slocum gliders', 'gliders','seawater'],
    packages=packages,
#    py_modules=[
#        'glider_utils.argos', 'conv', 'geo', 'seawater2', 'seawater3',
#        'parsers.dbd_parsers', 'parsers.dvl_parsers', 
#        'parsers.gliderstate_parser', 'parsers.log_parser',
#        'plots.enduranceMaps', 'plots.plots', 'plots.SingleGliderTracks',
#        'stats.days_of_gldata.'],
    package_data={'glider_utils.plots':['ETOPO*.mat']},
    requires=['numpy', 'matplotlib', 'pandas', 'gsw',
    'mpl_toolkits.basemap'],
)