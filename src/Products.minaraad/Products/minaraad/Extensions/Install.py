# -*- coding: utf-8 -*-

from StringIO import StringIO

import transaction
from Products.CMFCore.utils import getToolByName
from Products.SimpleAttachment.setuphandlers import \
    registerAttachmentsFormControllerActions
from collective.recaptcha.settings import IRecaptchaSettings

from Products.minaraad import config

MINARAAD_PROPERTIES = 'minaraad_properties'
out = StringIO()


def install(self, reinstall=False):
    """ External Method to install minaraad """
    print >> out, "Installation log of %s:" % config.PROJECTNAME

    from Products.minaraad.config import PRODUCT_DEPENDENCIES
    from Products.minaraad.config import PACKAGE_DEPENDENCIES
    portal = getToolByName(self, 'portal_url').getPortalObject()
    portal_quickinstaller = portal.portal_quickinstaller
    for product in PRODUCT_DEPENDENCIES + PACKAGE_DEPENDENCIES:
        if not portal_quickinstaller.isProductInstalled(product):
            portal_quickinstaller.installProduct(product)
            transaction.savepoint()

    portal_setup = getToolByName(self, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile(
        'profile-Products.minaraad:default')

    # Set up form controller actions for the widgets to work
    registerAttachmentsFormControllerActions(self)
    set_recaptcha_keys(self)
    print >> out, "Added actions for the attachment controls to the "
    print >> out, "base_edit form controller."

    # Add extra indexes.  Has been done in production a long time ago,
    # perhaps by hand, but now some new automated tests are failing
    # when we do not add the getItemstartdate index here.
    catalog = getToolByName(self, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (('getItemstartdate', 'DateIndex'),
              ('getCategory', 'FieldIndex'),
              ('getDate', 'DateIndex'),
              ('getStart_time', 'DateIndex'),
              ('published', 'FieldIndex'),
              )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            print >> out, "Added %s for field %s." % (meta_type, name)
    if len(indexables) > 0:
        print >> out, "Indexing new indexes %s." % ', '.join(indexables)
        catalog.manage_reindexIndex(ids=indexables)

    return out.getvalue()


def set_recaptcha_keys(context):
    """Set ReCaptchaKeys for site.
    """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    recaptcha = IRecaptchaSettings(portal)
    recaptcha.public_key = config.RECAPTCHA_PUBLIC_KEY
    recaptcha.private_key = config.RECAPTCHA_PRIVATE_KEY


def uninstall(self):
    out = StringIO()
    print >> out, 'no custom uninstall'
    return out.getvalue()
