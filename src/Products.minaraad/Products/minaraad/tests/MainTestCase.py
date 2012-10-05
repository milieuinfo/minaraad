from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.Five import fiveconfigure
from Zope2.App import zcml
from Products.PloneTestCase.layer import onsetup
from Products.minaraad.config import PRODUCT_DEPENDENCIES
from Products.minaraad.config import PACKAGE_DEPENDENCIES
from Products.minaraad.config import ROOT_CHILDREN
from Products.minaraad.tests.utils import _createNode


@onsetup
def setup_minaraad():
    """Set up the zcml and additional packages.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    fiveconfigure.debug_mode = True
    import Products.minaraad
    zcml.load_config('configure.zcml', Products.minaraad)
    fiveconfigure.debug_mode = False
    # Make all dependencies available for Zope:
    for dependency in PRODUCT_DEPENDENCIES:
        ztc.installProduct(dependency)
    for dependency in PACKAGE_DEPENDENCIES:
        ztc.installPackage(dependency)


from Products.PluggableAuthService.interfaces.plugins import \
    IRoleAssignerPlugin

# Call the deferred setup method, create a Plone Site and install minaraad.
setup_minaraad()
ztc.installProduct('minaraad')
ptc.setupPloneSite(products=['minaraad'])


class MainTestCase(ptc.PloneTestCase):
    """Base TestCase for minaraad."""

    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.loginAsPortalOwner()
        self._createFolderStructure()
        self.login('test_user_1_')

    def _createFolderStructure(self):
        """Create the initial folders in the root of the portal
        """
        portal = self.portal
        # first of all let's remove the object we don't want in the portal root
        itemsToRemove = ['news', 'events', 'Members']
        for item in itemsToRemove:
            if hasattr(portal, item):
                portal._delObject(item)
        # Now let's create the ones we want
        for node in ROOT_CHILDREN:
            _createNode(portal, node)

    def assureRoles(self, roles):
        """Assure that the given role exists in PAS

        It seems that without this, the addMember will
        silently fail. Roles must exist in the role manager.

        I don't know if this is a bug or not. (ree)
        """
        pas = self.portal.acl_users
        plugins = pas._getOb('plugins')
        roleassigners = plugins.listPlugins(IRoleAssignerPlugin)
        # XXX this will really yield the portal_role_manager.
        for roleassigner_id, roleassigner in roleassigners:
            for role in roles:
                if role not in roleassigner._roles:
                    roleassigner.addRole(role)


class MinaraadFunctionalTestCase(MainTestCase, ptc.FunctionalTestCase):
    pass
