import logging
import os
import urllib2

from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.MemberDataTool import MemberData
from Products.CMFCore.MembershipTool import MembershipTool
from Products.CMFCore.permissions import ChangeLocalRoles
from Products.CMFCore.utils import _checkPermission
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet
from recaptcha.client import captcha

logger = logging.getLogger('Products.minaraad')


def submit(*args, **kwargs):
    """
    Patch for recaptcha.client.captcha.submit to handle http proxy.
    """
    if os.environ.get('HTTP_PROXY'):
        proxy_support = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
    return captcha.old_submit(*args, **kwargs)


def set_last_modification_date(member):
    """Set the last_modification_date of the member.

    Adapted from PlonePAS.tools.memberdata.MemberData.setMemberProperties.
    """
    user = member.getUser()
    sheets = getattr(user, 'getOrderedPropertySheets', lambda: None)()

    # We won't always have PlonePAS users, due to acquisition,
    # nor are guaranteed property sheets
    if not sheets:
        return

    # If we got this far, we have a PAS and some property sheets.
    property_id = 'last_modification_date'
    value = DateTime()
    for sheet in sheets:
        if not sheet.hasProperty(property_id):
            continue
        if IMutablePropertySheet.providedBy(sheet):
            sheet.setProperty(user, property_id, value)
            break


# security.declareProtected(View, 'deleteLocalRoles')
# @postonly
def deleteLocalRoles(self, obj, member_ids, reindex=1, recursive=0,
                     REQUEST=None, depth=3):
    """ Delete local roles of specified members.

    This takes far too much memory.  See if we can reduce this.

    We add a depth on which we search.  This is a fluid depth.  If the
    object does not need deletion of local roles, we decrease the
    depth, thus eliminating uninteresting folders where the member
    likely has no local roles anywhere.
    """
    from time import time
    deleted = False
    if _checkPermission(ChangeLocalRoles, obj):
        for member_id in member_ids:
            if obj.get_local_roles_for_userid(userid=member_id):
                obj.manage_delLocalRoles(userids=member_ids)
                deleted = True
                break
    if not deleted:
        # Nothing deleted at this level.  Decrease depth.
        depth -= 1
        if depth <= 0:
            # Ignore the rest of this content tree, if any.
            logger.info("Ignoring %s and below.", '/'.join(obj.getPhysicalPath()))
            return

    time2 = time()

    if recursive and hasattr(aq_base(obj), 'contentValues'):
        for subobj in obj.contentValues():
            self.deleteLocalRoles(subobj, member_ids, 0, 1, depth=depth)

    time3 = time()
    if reindex:
        print("delete local roles everywhere: %f" % (time3 - time2))
    if reindex and hasattr(aq_base(obj), 'reindexObjectSecurity'):
        # reindexObjectSecurity is always recursive
        obj.reindexObjectSecurity()
        time4 = time()
        print("reindex object security: %f" % (time4 - time3))


def notifyModified(self):
    set_last_modification_date(self)
    return self._orig_notifyModified()


def patch_captcha():
    captcha.old_submit = captcha.submit
    captcha.submit = submit


def unpatch_captcha():
    captcha.submit = captcha.old_submit


def patch_memberdata():
    MemberData._orig_notifyModified = MemberData.notifyModified
    MemberData.notifyModified = notifyModified


def unpatch_memberdata():
    MemberData.notifyModified = MemberData._orig_notifyModified


def patch_membershiptool():
    MembershipTool._orig_deleteLocalRoles = MembershipTool.deleteLocalRoles
    MembershipTool.deleteLocalRoles = deleteLocalRoles


def unpatch_membershiptool():
    MembershipTool.deleteLocalRoles = MembershipTool._orig_deleteLocalRoles


def patch_all():
    patch_captcha()
    patch_memberdata()
    patch_membershiptool()


def unpatch_all():
    unpatch_captcha()
    unpatch_memberdata()
    unpatch_membershiptool()
