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


setup(name='Products.minaraad',
      version=version,
      description="Product for minaraad.be",
      long_description="Product for minaraad.be",
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok',
          'quintagroup.formlib.captcha',
      ],
)
