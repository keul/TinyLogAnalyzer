# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

setup(name='TinyLogAnalyzer',
      # scripts=['src/tinylogan',],
      version="0.4.0",
      description="Command line utility for perform response time analysis onto HTTP access logs",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: System Administrators",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Utilities",
                   "Topic :: Internet :: Log Analysis",
                   "Topic :: Internet :: WWW/HTTP",
                   ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='file apache log response-time analyser http access',
      author='keul',
      author_email='luca@keul.it',
      url='https://kpython-utils.svn.sourceforge.net/svnroot/kpython-utils/TinyLogAnalyzer/',
      license='GPL',
      # packages=find_packages('src', exclude=['ez_setup',]),
      py_modules=['tinylogan',],
      package_dir = {'': 'src'},
      include_package_data=True,
      #package_data={'': ['example_profile.cfg', ]},
      data_files=[('profiles', ['src/example_profile.cfg'])],
      zip_safe=False,
      install_requires=[
          'setuptools'
          # -*- Extra requirements: -*-
      ],
      entry_points={'console_scripts': ['tinylogan = tinylogan:main', ]}
      )

