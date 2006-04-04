## Script (Python) "isHomePage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

portalroot = context.portal_url.getPortalObject()
defaultpage = portalroot.restrictedTraverse(portalroot.getDefaultPage())
return context == defaultpage or context == portalroot

