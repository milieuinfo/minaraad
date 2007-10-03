"""
Use the mailPassword method of CMFPlone/RegistrationTool.py 3.0.

That way we can use the mail_password_template.pt of 3.0 which seems
to actually work, including translations.
"""

import logging
logger = logging.getLogger('Minaraad_monkey')

# imports for mailPassword
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo, Unauthorized
from smtplib import SMTPRecipientsRefused

# _checkEmail is acually defined seperately in 3.0, but there is no
# difference between that one and the one here:
from Products.CMFDefault.RegistrationTool import _checkEmail


security = ClassSecurityInfo()
security.declarePublic('mailPassword')
def mailPassword(self, forgotten_userid, REQUEST):
    """ Wrapper around mailPassword """
    membership = getToolByName(self, 'portal_membership')
    if not membership.checkPermission('Mail forgotten password', self):
        raise Unauthorized, "Mailing forgotten passwords has been disabled"

    utils = getToolByName(self, 'plone_utils')
    member = membership.getMemberById(forgotten_userid)

    if member is None:
        raise ValueError, 'The username you entered could not be found'

    # assert that we can actually get an email address, otherwise
    # the template will be made with a blank To:, this is bad
    email = member.getProperty('email')
    if not email:
        raise ValueError('That user does not have an email address.')
    else:
        # add the single email address
        if not utils.validateSingleEmailAddress(email):
            raise ValueError, 'The email address did not validate'
    check, msg = _checkEmail(email)
    if not check:
        raise ValueError, msg

    # Rather than have the template try to use the mailhost, we will
    # render the message ourselves and send it from here (where we
    # don't need to worry about 'UseMailHost' permissions).
    reset_tool = getToolByName(self, 'portal_password_reset')
    reset = reset_tool.requestReset(forgotten_userid)

    email_charset = getattr(self, 'email_charset', 'UTF-8')
    mail_text = self.mail_password_template( self
                                           , REQUEST
                                           , member=member
                                           , reset=reset
                                           , password=member.getPassword()
                                           , charset=email_charset
                                           )
    if isinstance(mail_text, unicode):
        mail_text = mail_text.encode(email_charset)
    host = self.MailHost
    try:
        host.send( mail_text )

        return self.mail_password_response( self, REQUEST )
    except SMTPRecipientsRefused:
        # Don't disclose email address on failure
        raise SMTPRecipientsRefused('Recipient address rejected by server')


# Do the monkey patch
import Products.CMFPlone.RegistrationTool
Products.CMFPlone.RegistrationTool.RegistrationTool.mailPassword = mailPassword
logger.info('*** registrationtool patch applied ***')
