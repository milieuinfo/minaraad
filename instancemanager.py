python = 'python2.4'
zope_version = '2.9.3' # INSTALL says 2.9.2, but lets try the latest.

archivebundle_sources = [
    'Plone-2.1.2.tar.gz',
    ]
symlink_sources = [
    'PasswordResetTool',
    'OrderableReferenceField',
    'PortalTransforms',
    'PloneTranslations',
    'minaraad',
    ]
archive_sources = [
    'FCKeditor.Plone2.2.zip',
    'RichDocument-2.0rc1.tar.gz',
    'TextIndexNG3-3.1.8.tar.gz',
    'DocFinderTab-1.0.0.tar.gz',
    'PloneTestCase-0.8.2.tar.gz',
    ]
plone_site_name = 'minaraad'
main_products = [
    'minaraad',
    ]
user = 'admin'
password = 'MinZope'

# See minaraad's INSTALL.txt for a few manual steps:
# - Small changes in translations
# - Possibly run the setup of TextIndexNG3 if you haven't previously
#   done so.
