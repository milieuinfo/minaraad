## Script (Python) "prefs_user_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, portrait='',delete_portrait=''
##title=Edit user
##

from Products.CMFPlone import PloneMessageFactory as _
from DateTime import DateTime

#update portrait
REQUEST=context.REQUEST
portal_membership = context.portal_membership
member=portal_membership.getMemberById(userid)
if portrait:
    portrait.seek(0)
    portal_membership.changeMemberPortrait(portrait, userid)

if delete_portrait:
    context.portal_membership.deletePersonalPortrait(member.getId())

processed={}
for id, property in context.portal_memberdata.propertyItems():
    if id == 'last_login_time':
        continue
    if REQUEST.has_key(id):
        processed[id] = REQUEST.get(id)

if not processed.get('ext_editor'):
    processed['ext_editor'] = ''

if not processed.get('listed'):
    processed['listed'] = ''

if not processed.get('visible_ids'):
    processed['visible_ids'] = 0

# Also set last modification date
processed['last_modification_date'] = DateTime()

context.plone_utils.setMemberProperties(member, **processed)

context.plone_utils.addPortalMessage(_(u'Changes made.'))
return state