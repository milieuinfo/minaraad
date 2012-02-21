## Script (Python) "getGlobalPortalRoles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# CHANGED compared to standard Plone: exclude not only Owner, but also
# ProjectMember.
return [r for r in context.portal_membership.getPortalRoles()
        if r != 'Owner' and r != 'ProjectMember']
