#! /usr/bin/env python
"""Python API to ship strip theory code Scores2"""

import codecs
import os

from setuptools import find_packages, setup

# get __version__ from _version.py
ver_file = os.path.join('pyscores2', '_version.py')
with open(ver_file) as f:
    exec(f.read())

DISTNAME = 'pyscores2'
DESCRIPTION = 'Python API to ship strip theory code Scores2'
with codecs.open('README.md', encoding='utf-8-sig') as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = 'Martin Alexandersson'
MAINTAINER_EMAIL = 'maa@sspa.se'
URL = 'https://github.com/martinlarsalbert/pyscores2'
LICENSE = 'GNU GPLv3'
DOWNLOAD_URL = 'https://github.com/martinlarsalbert/pyscores2'
VERSION = __version__
INSTALL_REQUIRES = ['pandas','matplotlib','scipy']
CLASSIFIERS = ['Intended Audience :: Science/Research',
               'Intended Audience :: Developers',
               'License :: OSI Approved',
               'Programming Language :: Python',
               'Topic :: Software Development',
               'Topic :: Scientific/Engineering',
               'Operating System :: Microsoft :: Windows',
               'Operating System :: POSIX',
               'Operating System :: Unix',
               'Operating System :: MacOS',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7']
EXTRAS_REQUIRE = {
    'tests': [
        'pytest',
        'pytest-cov'],
    'docs': [
        'sphinx',
        'sphinx-gallery',
        'sphinx_rtd_theme',
        'numpydoc',
    ]
}

package_data= {
          "pyscores2": [r"fortran/scores2.exe"],
          "pyscores2.test": [r'*.in', r'*.out']
      }

setup(name=DISTNAME,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      long_description=LONG_DESCRIPTION,
      zip_safe=False,  # the package can run out of an .egg file
      classifiers=CLASSIFIERS,
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      package_data=package_data,
       author="Martin Alexandersson",
      author_email='maralex@chalmers.se',
      python_requires='>=3.5',
      keywords='rolldecayestimators',
      )
