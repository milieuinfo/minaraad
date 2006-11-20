## Script (Python) "emailNotify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Notify members of new website
##

raise 'DEPRECATED SCRIPT, DO NOT USE IT ANY MORE.'

from Products.minaraad.utils.member import sendEmailForAllMembersWithEmail, getAllMembersWithoutEmail
from Products.CMFCore.permissions import ManagePortal
from AccessControl import Unauthorized

# First check if we have permission to go mailing everybody
membership = context.portal_membership
if not membership.checkPermission(ManagePortal, context):
    raise Unauthorized("Access Denied!")

# Start mailing everyone with email and 3 letter password
failed = sendEmailForAllMembersWithEmail(context)

print "Sending all members with old passwords a mail..."

if failed:
    print "Failed to send mail to the following recipients:"
    for f in failed:
        print f
else:
    print "No failures to deliver email"
print

# Next get all the users without email so we can call them
noemail = getAllMembersWithoutEmail(context)

if noemail:
    print "The following users had no e-mail adress (by user name):"
    for n in noemail:
        print n
else:
    print "All members have e-mail adresses. No further calling needed"

return printed

