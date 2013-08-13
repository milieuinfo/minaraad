from zope.component import getMultiAdapter
from zope.interface import implements

from zope.formlib import form
from plone.app.users.browser.register import RegistrationForm
from quintagroup.formlib.captcha import CaptchaWidget

from Products.minaraad.userdataschema import IRegisterForm, ICaptchaSchema


class PatchedCaptchaWidget(CaptchaWidget):
    # Temporary patch for issue
    # http://plone.org/products/plone-captchas/issues/6
    def _toFieldValue(self, input):
        value = super(PatchedCaptchaWidget, self)._toFieldValue(input)
        if isinstance(value, unicode):
            value = value.encode('ascii', 'ignore')
        return value


class MinaRegistrationForm(RegistrationForm):
    """ Subclass the standard registration form
    """
    implements(IRegisterForm)

    @property
    def form_fields(self):
        # Get the fields so we can fiddle with them
        myfields = super(MinaRegistrationForm, self).form_fields

        # Add a captcha field when the user is not logged in.  This is
        # the normal case for this register form, but we check it
        # explicitly, because there are problems with kss inline
        # validation which are best solved by only offering inline
        # validation for logged-in users.
        pps = getMultiAdapter((self.context, self.request),
                              name='plone_portal_state')
        if pps.anonymous():
            # Add a captcha field to the schema
            myfields += form.Fields(ICaptchaSchema)
            myfields['captcha'].custom_widget = PatchedCaptchaWidget

        # Perform any field shuffling here...

        # Return the fiddled fields
        return myfields
