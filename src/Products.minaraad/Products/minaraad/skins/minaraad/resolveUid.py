## Script (Python) "resolveUid"
## taken from kupu resolveuid (thx ...)
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Retrieve an object using its UID
##

# Modification: go to the /view pages of files so that you get filetype
# information and size information. Alternative would be to display this
# information inline, which means an extra transformation step. [reinout]

from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote

request = context.REQUEST
response = request.RESPONSE

uuid = traverse_subpath.pop(0)
reference_tool = getToolByName(context, 'reference_catalog')
obj = reference_tool.lookupObject(uuid)
if not obj:
    return context.standard_error_message(error_type=404,
     error_message='''The link you followed appears to be broken''')

if traverse_subpath:
    traverse_subpath.insert(0, obj.absolute_url())
    target = '/'.join(traverse_subpath)
else:
    target = obj.absolute_url()

# Modification starts here.
if obj.portal_type in ['File', 'FileAttachment']:
    target += '/view'
# End of modification.

if request.QUERY_STRING:
    target += '?' + request.QUERY_STRING

return response.redirect(target, status=301)
