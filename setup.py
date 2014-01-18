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

    scripts=[
        'scripts/rv_session_from_csv',
    ],

)
