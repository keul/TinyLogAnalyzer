# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

setup(name='TinyLogAnalyzer',
      # py_modules=['tinylogan',],
      scripts=['src/tinylogan',],
      version="0.2.0",
      description="Simple bash utility for analyse HTTP access log with enabled response time",
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
      keywords='file apache log analyser http access',
      author='keul',
      author_email='luca@keul.it',
      url='https://kpython-utils.svn.sourceforge.net/svnroot/kpython-utils/TinyLogAnalyzer/',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      package_dir = {'tinylogan':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

