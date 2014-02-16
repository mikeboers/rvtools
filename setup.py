from setuptools import setup, find_packages

setup(
    
    name='rvtools',
    version='0.1.0',
    description='Tools for working with Tweak Software\s RV.',
    url='http://github.com/mikeboers/rvtools',
    
    packages=find_packages(exclude=['tests', 'tests.*']),
    
    author='Mike Boers',
    author_email='rvtools@mikeboers.com',
    license='BSD-3',

    install_requires='''
        PyYAML
        wheel
    ''',

    entry_points=dict(
        console_scripts='''
            rvtools-wheel = rvtools.commands.wheel:main
            rvtools-build = rvtools.commands.build:main
            rvtools-install = rvtools.commands.install:main
            rvpkg2 = rvtools.package:main
    '''),

    scripts=[
        'scripts/rv_session_from_csv',
    ],

)
