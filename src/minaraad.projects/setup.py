from setuptools import setup, find_packages
import os

try:
    # Try reading the version.txt from the buildout directory.
    versionfile = open(os.path.join('..', '..', 'version.txt'))
    version = versionfile.read().strip()
    versionfile.close()
except IOError:
    # fallback
    version = '1.0'

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
