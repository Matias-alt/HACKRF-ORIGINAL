from distutils.core import setup
from setuptools.command.install import install
from setuptools import Extension

import subprocess

class CustomInstall(install):

    def initialize_options(self):
        install.initialize_options(self)
        self.compile = 1

        subprocess.check_call(["pyinstaller", "src/index.py", "--onefile", "--name", "hackrf-control"])

setup(
    name='hackrf-control',
    version='0.1.0',
    author='lastseal',
    author_email='hello@lastseal.com',
    scripts=['dist/hackrf-control'],
    cmdclass={
        'install': CustomInstall
    },
    ext_modules=[Extension('hackrf', sources = ['src/modules/hackrf.c'])]
)