from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

def install(self):
    out = StringIO()

    portal = getToolByName(self, 'portal_url').getPortalObject()
    
    newRoles = ('Raadslid',)
    for role in newRoles:
        if not portal._has_user_defined_role(role):
            portal._addRole(role)
            print >> out, "Added missing role '%s'" % role
        else:
            print >> out, "'%s' role already exists -- skipped" % role
            

    return out.getvalue()
