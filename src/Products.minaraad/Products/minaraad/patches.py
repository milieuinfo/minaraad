import os
import transaction
import urllib2

from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.MemberDataTool import MemberData
from Products.CMFCore.MembershipTool import MembershipTool
from Products.CMFCore.permissions import ChangeLocalRoles
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet
from recaptcha.client import captcha


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
                     REQUEST=None, obj_count=0):
    """ Delete local roles of specified members.

    This takes far too much memory.  See if we can reduce this.

    Example with ZopeFindAndApply:

    def fixOwnerTuple(obj, path):
        old = obj.getOwnerTuple()
        if old and old[0][-1] == 'portal_memberdata':
            new = (['acl_users'], old[1])
            logger.info('Repairing %s: %r -> %r' % (path, old, new))
            obj._owner = new
    portal.ZopeFindAndApply(portal, search_sub=True, apply_func=fixOwnerTuple)

    Well, might want to try the catalog.

    """
    if reindex:
        print("Using minaraad patch of deleteLocalRoles.")
    from time import time
    time1 = time()
    deleteLocalRolesSingleObject(obj, member_ids)
    time2 = time()
    obj_count += 1
    if reindex:
        print("main del local roles: %f" % (time2 - time1))
    if obj_count % 100 == 0:
        print("Saving sub transaction or savepoint. Object count %d" % obj_count)
        transaction.savepoint(optimistic=True)
        # Note that when searching on the Internet, you see references
        # to committing a sub transaction like this, but that is only
        # for ZODB 4 it seems.  It certainly fails with a TypeError
        # for us: transaction.commit(True)
    if recursive and hasattr(aq_base(obj), 'contentValues'):
        for subobj in obj.contentValues():
            obj_count = self.deleteLocalRoles(subobj, member_ids, 0, 1, obj_count=obj_count)

    time3 = time()
    if reindex:
        print("delete local roles everywhere: %f" % (time3 - time2))
    if reindex and hasattr(aq_base(obj), 'reindexObjectSecurity'):
        # reindexObjectSecurity is always recursive
        obj.reindexObjectSecurity()
    time4 = time()
    if reindex:
        print("reindex object security: %f" % (time4 - time3))
    return obj_count


def deleteLocalRolesSingleObject(obj, member_ids):
    """ Delete local roles of specified members.
    """
    if _checkPermission(ChangeLocalRoles, obj):
        for member_id in member_ids:
            if obj.get_local_roles_for_userid(userid=member_id):
                obj.manage_delLocalRoles(userids=member_ids)
                break


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
