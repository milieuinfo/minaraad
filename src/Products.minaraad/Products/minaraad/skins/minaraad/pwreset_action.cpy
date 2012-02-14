## Script (Python) "pwreset_action.cpy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Reset a user's password
##parameters=randomstring, userid=None, password=None, password2=None

from Products.CMFCore.utils import getToolByName
request = context.REQUEST

# Make it clear that the userid that is passed in should be used as a
# login name; also, we have made sure that all login names are lower
# case, so we should transform it here as well.
login_name = userid.lower()
status = "success"
pw_tool = getToolByName(context, 'portal_password_reset')
try:
    # Note: resetPassword expects a user id, but collective.emaillogin
    # has a patch that looks for a user id that matches the passed in
    # login name.
    pw_tool.resetPassword(login_name, randomstring, password)
except 'ExpiredRequestError':
    status = "expired"
except 'InvalidRequestError':
    status = "invalid"
except ValueError:
    status = "invalid"
else:
    # We need to figure out if a new user, or just resetting
    # If we are an old user, we are not logged in. So we go to "success".
    # If we are not logged in, then we override the normal plone behaviour,
    # and go to the subscription setup page (governed by status "newuser").
    # XXX I am not sure if the check works well in real life, or if it's needed
    mt = getToolByName(context, 'portal_membership')
    member = mt.getAuthenticatedMember()
    authenticated_id = member.getId()
    if not authenticated_id:
        # Note: this is also true for old members that have forgotten
        # their password.
        status = "newuser"
        # log in as that user (will update cookies)
        acl_users = getToolByName(context, 'acl_users')
        acl_users.updateCredentials(
            request, request.RESPONSE, login_name, password)

return state.set(status=status)
