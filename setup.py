from setuptools import setup

setup(
    name='cadmium',
    version='0.2',
    description='Mapping the CNC machining space to code',
    packages=['cadmium'],
    install_requires=[
        'numpy',
        'networkx',
        'pygcode',
        'more_itertools'
    ],
    license='GNU'
)