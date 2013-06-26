import os
import urllib2

from recaptcha.client import captcha
from DateTime import DateTime
from Products.CMFCore.MemberDataTool import MemberData
from Products.PlonePAS.interfaces.propertysheets import IMutablePropertySheet


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
            print 'setting last modification date'
            sheet.setProperty(user, property_id, value)
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


def patch_all():
    patch_captcha()
    patch_memberdata()


def unpatch_all():
    unpatch_captcha()
    unpatch_memberdata()
