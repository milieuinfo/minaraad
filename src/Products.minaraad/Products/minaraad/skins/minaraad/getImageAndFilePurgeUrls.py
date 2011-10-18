## Script (Python) "getImageAndFilePurgeUrls"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get extra urls to purge for ATImage and ATFile downloads

# Modification by reinout to standard cachefu script:
# * Reacting on FileAttachment and AnnualReport as on File.
# * Added /attachment_as_html as extra purge url

# TODO: this script is used by the files/images rule: enable it also
# on FileAttachment and AnnualReport. [reinout]

if not context.portal_type in ('Image', 'File',
                               'FileAttachment', 'AnnualReport'):
    return []
url_tool = context.portal_url
obj_url = url_tool.getRelativeUrl(context)
if context.portal_type in ['File', 'FileAttachment', 'AnnualReport']:
    suffixes = ['/download', '/attachment_as_html']
elif context.portal_type == 'Image':
    field = context.getField('image')
    scalenames = field.getAvailableSizes(context)
    suffixes = ['/image_' + s for s in scalenames]
return [obj_url + s for s in suffixes]
