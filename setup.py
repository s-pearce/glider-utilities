from distutils.core import setup

setup(
    name='compass_check',
    version='1.0',
    description='Glider Compass Checking Program',
    author='Stuart Pearce',
    author_email='spearce@coas.oregonstate.edu',
    py_modules=[
        'compass_check', 'cc.serial_rf',
        'cc.parse_options', 'cc.dockserver_com'],
    package_data={'cc': ['pickles/']},
    requires=['numpy', 'matplotlib', 'serial', 'dockserverTalk'],
)