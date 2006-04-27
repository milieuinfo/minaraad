# -*- coding: iso-8859-1 -*-

from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

SUBJECT = "Nieuwe website"
EMAILCONTENTS = \
"""
Beste %(gender)s %(fullname)s!

De Minaraad heeft een nieuwe website. Het adres is hetzelfde gebleven
-- http://www.minaraad.be -- maar de vormgeving, de structuur en de
mogelijkheden van de site zijn grondig veranderd en verbeterd. Zo
bevat de site voortaan een zoekfunctie (rechtsbovenaan) en kan u op al
onze producten abonneren. De voorkeuren van uw abonnement kan u zelf
instellen en wijzigen. Hiertoe dient de inlogfunctie linksonderaan de
website.

U hebt zich in het verleden geabonneerd op onze elektronische
nieuwsbrief of onze persberichten. Bij deze geven wij u een
inlognaam en initiele paswoord mee.

Inlognaam: %(id)s
Paswoord: %(password)s

Als u deze invoert dan kan u uw persoonsgegevens controleren, het
paswoord wijzigen en nadien uw productvoorkeuren kenbaar maken.

Op deze wijze kunnen wij u informatie op maat aanbieden.

Dank voor het vertrouwen in de Minaraad.

Met vriendelijke groet

Het Minaraadteam
"""

class fuzzydict(dict):
    DEFAULT = ''

    def __getitem__(self, key):
        try:
            value = super(fuzzydict, self).__getitem__(key)
        except KeyError:
            return self.DEFAULT
        else:
            return value


def getAllMembersWithThreeLetterPassword(context):
    members = []
    allmembers = getToolByName(context, 'portal_membership').listMembers()
    uf = getToolByName(context, 'acl_users')
    for member in allmembers:
        name = member.getProperty('id')
        autopass = makeMagicPassword(name)
        if member.authenticate(autopass, None):
            members.append(member)
    return members

def getAllMembersWithEmail(context):
    return [m for m in getAllMembersWithThreeLetterPassword(context)
            if m.getProperty('email')]

def getAllMembersWithoutEmail(context):
    return [m for m in getAllMembersWithThreeLetterPassword(context)
            if not m.getProperty('email')]

def makeMagicPassword(username): 
    autopass = list(username[-3:])
    autopass.reverse()
    return ''.join(autopass)

def sendEmailForAllMembersWithEmail(context):
    failedMembers = []
    mailhost = getToolByName(context, 'MailHost')
    mship = getToolByName(context, 'portal_membership')
    portal = getToolByName(context, 'portal_url').getPortalObject()
    fromAddr = portal.getProperty('email_from_address')
    fromName = portal.getProperty('email_from_name')
    for member in getAllMembersWithEmail(context):
        props = fuzzydict(member.__dict__.copy())
        props['password'] = makeMagicPassword(member.getProperty('id'))
        message = EMAILCONTENTS % (props)
        to = member.getProperty('email')
        try:
            mailhost.send(message=message,
                          mto=to,
                          mfrom='%s <%s>' % (fromName, fromAddr),
                          subject=SUBJECT)
        except ConflictError:
            raise
        except Exception, e:
            failedMembers.append((member, str(e)))

    return failedMembers
