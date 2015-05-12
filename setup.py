from setuptools import setup, find_packages

setup(
    name='pathpicker',
    version = '0.5.6',
    package_dir = {'': 'src'},
    packages = find_packages(exclude='src/tests*'),
)
