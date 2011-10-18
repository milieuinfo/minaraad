'''\
Service utilities

to be used by Manager only
'''

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.PlonePAS.interfaces.plugins import IUserManagement
from zope.cachedescriptors.property import Lazy
from ZODB.POSException import ConflictError

from Products.minaraad.config import TITLE_VOCAB
from Products.minaraad.browser.utils import email_logger

import logging
logger = logging.getLogger('Minaraad Service Utilities')


class ServiceUtils(BrowserView):

    members_deleted = None
    double_emails = None
    bad_emails = None
    changed_members = None
    changed_members_called = False
    changed_by_date = DateTime('2000/01/01')

    def __call__(self):
        if self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST':
            if self.request.get('form.button.DeleteMembers'):
                self.members_deleted = self.deleteMembersWithEmptyEmail()
            if self.request.get('form.button.FindDoubleEmails'):
                self.double_emails = self.find_double_emails()
            if self.request.get('form.button.FindBadEmails'):
                self.bad_emails = self.find_bad_emails()
            if self.request.get('form.button.ShowChangedMembers'):
                # Show members changed since one month
                today = DateTime().earliestTime()
                self.changed_by_date = today - 30
                self.changed_members = self.find_changed_members()
                self.changed_members_called = True
            if self.request.get('form.button.ShowAllChangedMembers'):
                self.changed_members = self.find_changed_members()
                self.changed_members_called = True
            if self.request.form.get('switch_to_email'):
                self.switched_to_email = self.switch_to_email()
            if self.request.form.get('switch_to_userid'):
                self.switched_to_userid = self.switch_to_userid()
        return self.index()

    def find_double_emails(self):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        members = portal_membership.listMembers()
        emails = {}
        for member in members:
            email = member.getProperty('email')
            if emails.get(email) is None:
                emails[email] = []
            emails[email].append(member.getId())

        return [(email, ids) for (email, ids) in emails.items()
                if len(ids) > 1]

    def find_bad_emails(self):
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')
        reg_tool = getToolByName(context, 'portal_registration')
        members = portal_membership.listMembers()
        emails = []
        for member in members:
            email = member.getProperty('email')
            member_id = member.getId()
            if not reg_tool.isValidEmail(email):
                emails.append((email, member_id))
            if not reg_tool.isMemberIdAllowed(email) and \
                    member_id != email:
                emails.append((email, member_id))

        return emails

    def deleteMembersWithEmptyEmail(self):
        'Delete all members with no email address'
        mt = getToolByName(self, 'portal_membership')
        acl = getToolByName(self, 'acl_users')
        all_members = mt.listMembers()
        members_without_email = [m for m in all_members
                                 if not m.getProperty('email')
                                 or not '@' in m.getProperty('email')]

        logger.info('Found %i members without email, proceed to delete...' %
                    (len(members_without_email), ))
        for member in members_without_email:
            id = member.getId()
            logger.info('Deleting member "%s"' % (id, ))
            acl.userFolderDelUsers([id])
        logger.info('Finished deleting %i members' %
                    (len(members_without_email), ))
        return 'Deleted %i members' % (len(members_without_email), )

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
                url=portal.absolute_url() + '/prefs_user_details?userid=' \
                    + member.getId(),
                fullname=fullname,
                )
            result.append(info)
        return result

    @property
    def _email_list(self):
        context = aq_inner(self.context)
        pas = getToolByName(context, 'acl_users')
        emails = {}
        for user in pas.getUsers():
            if user is None:
                # Created in the ZMI?
                continue
            email = user.getProperty('email', '')
            if email:
                if email not in emails.keys():
                    emails[email] = []
                emails[email].append(user.getUserId())
            else:
                logger.warn("User %s has no email address.", user.getUserId())
        return emails

    @Lazy
    def _plugins(self):
        """Give list of proper IUserManagement plugins that can update a user.
        """
        context = aq_inner(self.context)
        pas = getToolByName(context, 'acl_users')
        plugins = []
        for plugin_id, plugin in pas.plugins.listPlugins(IUserManagement):
            if hasattr(plugin, 'updateUser'):
                plugins.append(plugin)
        if not plugins:
            logger.warn("No proper IUserManagement plugins found.")
        return plugins

    def _update_login(self, userid, login):
        """Update login name of user.
        """
        for plugin in self._plugins:
            try:
                plugin.updateUser(userid, login)
            except KeyError:
                continue
            else:
                logger.info("Gave user id %s login name %s",
                            userid, login)
                return 1
        return 0

    def switch_to_email(self):
        if not self._plugins:
            return 0
        success = 0
        for email, userids in self._email_list.items():
            if len(userids) > 1:
                logger.warn("Not setting login name for accounts with same "
                            "email address %s: %r", email, userids)
                continue
            for userid in userids:
                success += self._update_login(userid, email)
        return success

    def switch_to_userid(self):
        context = aq_inner(self.context)
        pas = getToolByName(context, 'acl_users')
        if not self._plugins:
            return 0
        success = 0
        for user in pas.getUsers():
            if user is None:
                # Created in the ZMI?
                continue
            userid = user.getUserId()
            success += self._update_login(userid, userid)
        return success


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
