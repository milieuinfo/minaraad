from setuptools import setup, find_packages
import os


def get_file_contents_from_main_dir(filename):
    file_path = os.path.join('minaraad', 'projects', filename)
    this_file = open(file_path)
    contents = this_file.read().strip()
    this_file.close()
    return contents

version = get_file_contents_from_main_dir('version.txt')

setup(name='minaraad.projects',
      version=version,
      description="",
      long_description="",
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Zest software',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['minaraad'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'borg.localrole',
          'pyPDF',
          'reportlab'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
