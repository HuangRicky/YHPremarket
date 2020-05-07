from setuptools import (setup, find_packages)
# from distutils.util import convert_path
#
# main_ns = {}
# ver_path = convert_path('version.py')
# with open(ver_path) as ver_file:
#     exec(ver_file.read(), main_ns)

from YHPremarket import __version__

setup(
    name='YHPremarket',
    version=__version__,
    packages=find_packages(include=['YHPremarket']),
    install_requires=['pandas', 'requests', 'bs4'],
    # package_data={'YHPremarket': ['data/*']},
    url='http://github.com',
    license='MIT',
    author='Ruokun Huang',
    author_email='hruokun.2008@gmail.com',
    description='Yahoo Finance Pre-market and After-hours price parser'
)
