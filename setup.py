from setuptools import setup, find_packages
import sys, os

setup(name='map_analysis',
      version="0.1",
      description="Python implementation of map_analysis",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Shohei Mishima, Daisuke Takahashi',
      author_email='stumble.on.the.stair@gmail..com',
      url='https://github.com/Daisuke0209/map_analysis.git',
      license='BSD',
      packages='',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'protobuf'
      ],
      extras_require={
        'test': ['pytest'],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )