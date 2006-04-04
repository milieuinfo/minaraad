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
indexpage = portalroot.restrictedTraverse('index_html')
# ^^^ This might need a safety mechanism for when index_html doesn't exist
return context == defaultpage or context == indexpage

