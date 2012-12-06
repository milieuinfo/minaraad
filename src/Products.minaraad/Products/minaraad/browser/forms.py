from zope.interface import implements

from zope.formlib import form
from plone.app.users.browser.register import RegistrationForm
from quintagroup.formlib.captcha import CaptchaWidget

from Products.minaraad.userdataschema import IRegisterForm, ICaptchaSchema


class MinaRegistrationForm(RegistrationForm):
    """ Subclass the standard registration form
    """
    implements(IRegisterForm)

    @property
    def form_fields(self):
        # Get the fields so we can fiddle with them
        myfields = super(MinaRegistrationForm, self).form_fields

        # Add a captcha field to the schema
        myfields += form.Fields(ICaptchaSchema)
        myfields['captcha'].custom_widget = CaptchaWidget

        # Perform any field shuffling here...

        # Return the fiddled fields
        return myfields
