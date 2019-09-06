from distutils.core import setup

setup(
    name='glider_utils',
    version='1.0',
    description='Suite of Slocum Glider Python Utilities',
    author='Stuart Pearce',
    author_email='spearce@coas.oregonstate.edu',
    py_modules=[
        'argos', 'conv', 'geo', 'seawater2', 'seawater3',
        'parsers.dbd_parsers', 'parsers.dvl_parsers', 
        'parsers.gliderstate_parser', 'parsers.log_parser',
        'plots.enduranceMaps', 'plots.plots', 'plots.SingleGliderTracks',
        'stats.days_of_gldata.'],
    package_data={},
    requires=['numpy', 'matplotlib', 'pandas', 'gsw'],
)