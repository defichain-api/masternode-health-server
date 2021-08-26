from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='masternode_health',
    version='0.2.1',
    author='Christian Sandrini',
    author_email='mail@chrissandrini.ch',
    packages=find_packages(include=['masternode_health', 'masternode_health.*']),
    url='http://pypi.python.org/pypi/masternode_health',
    license='LICENSE.md',
    description='This script is designed for collecting server & DeFiChain node information of your system and send them to the DeFiChain Masternode Health API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['psutil'],
    entry_points={
        'console_scripts': ['masternode-health=masternode_health.monitor:main']
    },
    python_requires='>2.7'
)
