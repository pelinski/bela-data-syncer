from setuptools import setup
import os
import codecs

# import packages from Pipfile (from https://github.com/lewiswolf/kac_drumset/blob/master/setup.py)
this = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(this, 'Pipfile'), encoding='utf-8') as raw_pipfile:
    packages = []
    # read the Pipfile
    pipfile = raw_pipfile.readlines(1)
    raw_pipfile.close()
    # loop over the file
    is_pkg = False
    for line in pipfile:
        line = line.replace('\n', '')
        if not line:
            continue
        # find [packages]
        if line[0] == '[':
            if line == '[packages]':
                is_pkg = True
                continue
            else:
                is_pkg = False
                continue
        # append package names with required version
        if is_pkg:
            line_arr = line.split()
            packages.append(f'{line_arr[0]}{line_arr[2][1:-1] if line_arr[2][1:-1] != "*" else ""}')

setup(
    name='bela-data-syncer',
    version='0.0',
    description='Syncs sensor data across Belas',
    author='Teresa Pelinski',
    author_email='teresapelinski@gmail.com',
    packages=['DataSyncer'],
    install_requires=packages,  #external packages acting as dependencies
)