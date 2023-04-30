from setuptools import setup

setup(
    name='cadmium',
    version='0.1',
    description='Represent 3 axis cartesian milling machine operations with code',
    packages=['cadmium'],
    install_requires=[
        'numpy',
        'networkx',
        'pygcode',
        'more_itertools'
    ],
    license='GNU'
)