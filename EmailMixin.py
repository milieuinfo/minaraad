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
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import log_exc, log
from Products.minaraad.subscriptions import SubscriptionManager
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from DateTime import DateTime
##/code-section module-header

schema = Schema((

    TextField(
        name='body',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label='Body',
            label_msgid='minaraad_label_body',
            i18n_domain='minaraad',
        ),
        default_output_type='text/html'
    ),

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
        
        if self.getEmailSent() is not None:
            raise AlreadySentError("Content object at '%s' has already had " \
                                   "an e-mail sent" \
                                   % '/'.join(self.getPhysicalPath()))

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
        for member in members:
            emailBody = self.getEmailBody(member=member, context=self)

            if text:
                emailBody['text/plain'] += "Additional Message: %s" % text
                
                emailBody['text/html'] += '''
                <dl>
                <dt style="font-weight: bold">Additional Message</dt>
                <dd>%s</dd>
                </dl>
                ''' % text
            
            message = MIMEMultipart('alternative')
        
            textPlain = unicode(emailBody['text/plain'], charset)
            message.attach(MIMEText(textPlain, 'plain', charset))
        
            textHtml = unicode(emailBody['text/html'], charset)
            message.attach(MIMEText(textHtml, 'html', charset))
        
            message = str(message)
        
            try:
                mailHost.send(message = message,
                              mto = member.email,
                              mfrom = fromAddress,
                              subject = subject)
            except:
                log_exc('Could not send email from %s to %s regarding issue ' \
                        'in tracker %s\ntext is:\n%s\n' \
                        % (fromAddress, member.address, self.absolute_url(), emailBody,))
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
        portal_transforms = getToolByName(self, 'portal_transforms')
        plain = portal_transforms.convertTo('text/plain', cooked).getData()
        
        body = {
            'text/html': cooked,
            'text/plain': plain,
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
        return self.getBody()


# end of class EmailMixin

##code-section module-footer #fill in your manual code here
##/code-section module-footer



