'''\
Service utilities

to be used by Manager only
'''

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from ZODB.POSException import ConflictError

from Products.minaraad.config import TITLE_VOCAB
from Products.minaraad.utils import email_logger

import logging
logger = logging.getLogger('Minaraad Service Utilities')


class ServiceUtils(BrowserView):

    double_emails = None
    double_emails_called = False
    changed_members = None
    changed_members_called = False
    changed_by_date = DateTime('2000/01/01')

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            if self.request.get('form.button.FindDoubleEmails'):
                self.double_emails = self.find_double_emails()
                self.double_emails_called = True
            if self.request.get('form.button.ShowChangedMembers'):
                # Show members changed since one month
                today = DateTime().earliestTime()
                self.changed_by_date = today - 30
                self.changed_members = self.find_changed_members()
                self.changed_members_called = True
            if self.request.get('form.button.ShowAllChangedMembers'):
                self.changed_members = self.find_changed_members()
                self.changed_members_called = True
        return self.index()

    def find_double_emails(self):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        members = portal_membership.listMembers()
        emails = {}
        for member in members:
            email = member.getProperty('email').lower()
            if emails.get(email) is None:
                emails[email] = []
            emails[email].append(member.getId())

        return [(email, ids) for (email, ids) in emails.items()
                if len(ids) > 1]

    def resetMemberDataTitle(self):
        'Overwrite the title selection for members in the memberdata'
        md = getToolByName(self, 'portal_memberdata')
        # special care for our selection property gender
        md._updateProperty('genders', TITLE_VOCAB)
        logger.info('"Genders" property of memberdata tool is reset.')
        return '"Genders" property of memberdata tool is reset.'

    def addMemberDataLastModification(self):
        'add last_modification_date to the memberdata'
        md = getToolByName(self, 'portal_memberdata')
        if 'last_modification_date' not in md.propertyIds():
            md.manage_addProperty('last_modification_date', '2000/01/01',
                                  'date')
        msg = '"last_modification_date" property of memberdata tool is added.'
        logger.info(msg)
        return msg

    def find_changed_members(self):
        """Return a list of members that have (recently) been modified.
        """
        context = aq_inner(self.context)
        memship = getToolByName(context, 'portal_membership')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        members = memship.listMembers()

        changed_members = [
            (m.getProperty('last_modification_date'), m) for m in members
            if m.getProperty('last_modification_date') > self.changed_by_date]
        # Sort by modification date:
        changed_members = sorted(changed_members)
        result = []
        for date, member in changed_members:
            fullname = "%s %s %s" % (
                member.getProperty('gender'),
                member.getProperty('firstname'),
                member.getProperty('fullname'),
                )
            info = dict(
                modified=date.strftime('%Y-%m-%d'),
                url=(portal.absolute_url() + '/prefs_user_details?userid='
                     + member.getId()),
                fullname=fullname,
                )
            result.append(info)
        return result


SUBJECT = "Minaraad website: nieuwe inlogprocedure"
EMAILCONTENTS = \
"""
%(salutation)s

De inlogprocedure van de Minaraad website is vereenvoudigd. U hoeft nu
geen aparte gebruikersnaam meer te onthouden.  In plaats daarvan kunt U
direct inloggen met uw e-mailadres:

%(email)s

Als u uw wachtwoord vergeten bent, klik dan op de website op de link
'Wachtwoord vergeten'.

Zodra u bent ingelogd, kan u uw persoonsgegevens controleren,
eventueel het wachtwoord wijzigen en nadien uw productvoorkeuren
kenbaar maken.  Ga voor het wijzigen van uw gegevens naar --
http://www.minaraad.be/plone_memberprefs_panel --

Op deze wijze kunnen wij u informatie op maat aanbieden.

Dank voor het vertrouwen in de Minaraad.

Met vriendelijke groet

Het Minaraadteam
"""


class SendEmailToAllMembers(ServiceUtils):

    def __call__(self):
        email_logger.info("Starting emaillogin email.")
        dry_run = bool(int(self.request.get('dry_run', 1)))
        info = ["Starting emailing..."]
        if dry_run:
            message = "Dry run selected, only mailing Jurgen and Ignace."
            email_logger.info(message)
            info.append(message)
            info.append("Add '?dry_run=0' to the url to send to all members.")
        failed = self.send_email(dry_run)
        if failed:
            email_logger.warn("Sending failed to %d addresses." % len(failed))
            info.append("Sending failed to these addresses:")
            for address, error in failed:
                info.append("%s: %s", address, error)
        else:
            info.append("Sending was successfull.")
        email_logger.info("End of emaillogin email sending.")
        return '\n'.join(info)

    def send_email(self, dry_run=True):
        failedMembers = []
        context = aq_inner(self.context)
        mailhost = getToolByName(context, 'MailHost')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        fromAddr = portal.getProperty('email_from_address')
        fromName = portal.getProperty('email_from_name')

        double_emails = [i[0] for i in self.find_double_emails()]
        allmembers = getToolByName(context, 'portal_membership').listMembers()
        for member in allmembers:
            if dry_run:
                if member.getId() not in ('ignace.decancq', 'jurgenisdenaam'):
                    continue
            allmembers = allmembers[:2]
            email = member.getProperty('email')
            if email in double_emails:
                email_logger.warn(
                    "Not sending mail to duplicate email address: %s",
                    email)
                continue
            first_name = member.getProperty('firstname', '').strip()
            if first_name:
                salutation = "Beste %s," % first_name
            else:
                salutation = ("Geachte Meneer/Mevrouw %s," %
                              member.getProperty('fullname', ''))
            props = dict(salutation=salutation,
                         email=email)
            message = EMAILCONTENTS % (props)
            try:
                mailhost.send(message=message,
                              mto=email,
                              mfrom='%s <%s>' % (fromName, fromAddr),
                              subject=SUBJECT)
            except ConflictError:
                raise
            except Exception, e:
                email_logger.warn(
                    "Sending to member %s failed with exception: %r",
                    member.getProperty('id'), str(e))
                failedMembers.append((member.getProperty('id'), str(e)))
            else:
                email_logger.info("Successfully sent email to %s", email)

        return failedMembers
