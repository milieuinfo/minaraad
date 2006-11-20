# -*- coding: utf-8 -*-
#
# File: EmailMixin.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.5.0 svn/devel
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Rocky Burt <r.burt@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.minaraad.config import *

##code-section module-header #fill in your manual code here
import types
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import log_exc, log
from Products.minaraad.subscriptions import SubscriptionManager
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from DateTime import DateTime
import logging, os

# Arrange logging
logger = logging.getLogger('minaraad_email')
# Also log these messages to a separate file
# XXX this may be possible through zope.conf too but I can't figure out
logpath = '%(INSTANCE_HOME)s/log/minaraad_email.log' % os.environ
hdlr = logging.FileHandler(logpath)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

class DictLike(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

##/code-section module-header

schema = Schema((

    DateTimeField(
        name='emailSent',
        widget=CalendarWidget(
            visible=-1,
            label='Emailsent',
            label_msgid='minaraad_label_emailSent',
            i18n_domain='minaraad',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

EmailMixin_schema = schema.copy()

##code-section after-schema #fill in your manual code here
class AlreadySentError(Exception):
    pass
##/code-section after-schema

class EmailMixin:
    """
    """
    security = ClassSecurityInfo()

    allowed_content_types = []
    _at_rename_after_creation = True

    schema = EmailMixin_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('email')
    def email(self, text='', additionalMembers=(), testing=False):
        """
        Take the result from getEmailBody (an abstract method) and email
        to appropriate persons.
        """
        
        """
        # We don't care anymore if an email has already been sent, so we ignore this check.
        if self.getEmailSent() is not None:
            raise AlreadySentError("Content object at '%s' has already had " \
                                   "an e-mail sent" \
                                   % '/'.join(self.getPhysicalPath()))
        """
        tool = getToolByName(self, 'portal_membership')
        members = [tool.getMemberById(memberid)
                   for memberid in additionalMembers]

        if not testing:
            sm = SubscriptionManager(self)
            members = [member for member in
                       sm.emailSubscribers(self.getSubscriptionId())] + \
                       members
            self.setEmailSent(DateTime())
            
        
        portal = getToolByName(self, 'portal_url').getPortalObject()
        plone_utils = getToolByName(portal, 'plone_utils')
        charset = plone_utils.getSiteEncoding()
        
        fromAddress = portal.getProperty('email_from_address')
        
        subject = '[%s] %s' % (portal.title_or_id(), self.Title())
        
        mailHost = getToolByName(portal, 'MailHost')
        
        failed_postings = []

        for member in members:
            emailBody = self.getEmailBody(member=member, context=self)

            if text:
                emailBody['text/plain'] += "\n%s" % text
                
                emailBody['text/html'] += '''
                <br />
                <br />
                <br />
                %s
                ''' % text
            
            message = MIMEMultipart('alternative')
            message.attach(MIMEText(emailBody['text/plain'], 'plain', charset))
            message.attach(MIMEText(emailBody['text/html'], 'html', charset))
            message = str(message)
        
            send_info = DictLike(
                path = self.absolute_url(),
                message = emailBody,
                subject = subject,
                fromAddress = fromAddress,
                member = member,
                toAddress = member.getProperty('email', 'N/A (%s)' % member.getProperty('id')),
                )

            try:
                mailHost.send(message = message,
                              mto = member.getProperty('email', ''),
                              mfrom = fromAddress,
                              subject = subject)
            except Exception, exc:
                # XXX traceback is not needed now
                #log_exc('Could not send email from %(fromAddress)s to %(toAddress)s regarding issue ' \
                #        'in tracker %(path)s\ntext is:\n%(message)s\n' % send_info.__dict__)
                send_info.excname = str(exc.__class__.__name__)
                send_info.exctxt = str(exc)
                logger.log(logging.ERROR, 'Template %(path)s email failed sending from %(fromAddress)s to %(toAddress)s (%(excname)s: %(exctxt)s)' % send_info.__dict__)
                failed_postings.append(send_info);
            else:
                logger.log(logging.INFO, 'Template %(path)s email succesfully sent from %(fromAddress)s to %(toAddress)s' % send_info.__dict__)

        # Post a fake entry to error_log.
        # this enables to see failed postings from the ZMi, without the need
        # for an extra tool.
        # XXX Attention! Zope restart clears content of the error_log.
        # XXX increase "Number of exceptions to keep" from 20 to like 100
        if failed_postings:
            # post an entry to error_log (fake!)
            info = []
            info.append('Errors when sending out template %(path)s from %(fromAddress)s' % failed_postings[0].__dict__)
            info.append('')
            info.append('To:\t\t\tException:'.expandtabs())
            for posting in failed_postings:
                info.append(('%(toAddress)s\t\t%(excname)s: %(exctxt)s' % send_info.__dict__).expandtabs())
            info.append('')
            info.append('%d errors in total' % len(failed_postings))
            # insert it
            error_log = getToolByName(self, 'error_log')
            error_log.raising(['EmailSendError', 'This is not a real exception. See information below.', '\n'.join(info)])
        # return failed members
        return failed_postings

    security.declarePublic('getEmailBody')
    def getEmailBody(self, *args, **kwargs):
        """
        Return both plain and html versions (a dict with keys
        'text/plain' and 'text/html') of an appropriate email template. 
        Default implementation will cook the template from schema field
        emailTemplate.
        """
        template = getattr(self, self.getTemplateName(), None)
        if template is None:
            template = getattr(self, "EmailTemplate-Default", None)

        cooked = template.pt_render(extra_context=kwargs)
        cooked = fixRelativeUrls(cooked, getToolByName(self, 'portal_url')())
        portal_transforms = getToolByName(self, 'portal_transforms')
        
        body = {
            'text/html': cooked,
            'text/plain': portal_transforms('lynx_dump', cooked),
        }

        return body

    security.declarePublic('getSubscriptionId')
    def getSubscriptionId(self):
        """
        Returns the subscription id.  By default, this implementation
        will derive the subscription id from the class name.
        """
        
        return self.__class__.__name__
        
    # Manually created methods

    def getTemplateName(self):
        return "EmailTemplate-%s" % self.getPortalTypeName()
    
    security.declarePublic('getEmailContentsFromContent')
    def getEmailContentsFromContent(self):
        """Override this in your Content Types to add HTML to the
        outgoing e-mail.
        """
        return "<div>%s</div>" % self.getBody()


# end of class EmailMixin

##code-section module-footer #fill in your manual code here
def fixRelativeUrls(xml, portal_url):
    return xml.replace('./resolveUid', portal_url + '/resolveUid')
##/code-section module-footer



