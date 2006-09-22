from ZODB.POSException import ConflictError
import AccessControl

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from Products.minaraad.config import TITLE_VOCAB


SUBJECT = "Nieuwe website"
EMAILCONTENTS = \
"""
%(salutation)s

Zoals we eerder al communiceerden, heeft de Minaraad een nieuwe
website. Daar het besturingssysteem van de website gloednieuw is,
hadden we gedurende de eerste weken wat last van kinderziektes.  Nu
zijn deze opgelost..

Bij deze geven wij u een inlognaam en initieel paswoord mee.

Inlognaam: %(id)s
Paswoord: %(password)s

Als u deze invoert dan kan u uw persoonsgegevens controleren, het
paswoord wijzigen en nadien uw productvoorkeuren kenbaar maken.  Ga
voor het wijzigen van uw gegevens naar --
http://www.minaraad.be/plone_memberprefs_panel --

Op deze wijze kunnen wij u informatie op maat aanbieden.

Dank voor het vertrouwen in de Minaraad.

Met vriendelijke groet

Het Minaraadteam
"""
from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo('Products.minaraad.utils.member')

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

security.declarePublic('getAllMembersWithoutEmail')
def getAllMembersWithoutEmail(context):
    return [m for m in getAllMembersWithThreeLetterPassword(context)
            if not m.getProperty('email')]

def makeMagicPassword(username): 
    autopass = list(username[-3:])
    autopass.reverse()
    return ''.join(autopass)

security.declarePublic('sendEmailForAllMembersWithEmail')
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
        if props['firstname'].strip():
            props['salutation'] = "Beste %s!" % props['firstname']
        else:
            props['salutation'] = ("Geachte Meneer/Mevrouw %s," %
                                   props['fullname'])
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
            failedMembers.append((member.getProperty('id'), str(e)))

    return failedMembers

def getAllMembersWithNonVocabularyTitleByTitle(context):
    result = {}
    mship = getToolByName(context, 'portal_membership')
    for member in mship.listMembers():
        title = member.getProperty('gender')
        if title not in TITLE_VOCAB:
            l = result.setdefault(title, [])
            l.append(member)
    return result

def mapNonVocabularyTitles(membersbytitle):
    mapping = {
        'Dr. ir.': 'Dr. Ir.',
        'Ir': 'Ir.',
        'Mevr.': 'Mevrouw',
        'Dir. Ir': 'Dir. Ir.',
        'Prof. dr.': 'Prof. Dr.',
        'Em. Prof. dr.': 'Em. Prof. Dr.',
        'Prof. dr. ir.': 'Prof. Dr. Ir.',
        }
    for title, members in membersbytitle.items():
        newtitle = mapping.get(title, title)
        if newtitle != title:
            for m in members:
                m.setMemberProperties({'gender': newtitle})

security.declarePublic('doConvertGenderToBeVocabularyConform')
def doConvertGenderToBeVocabularyConform(context):

    membership = context.portal_membership
    if not membership.checkPermission(permissions.ManagePortal, context):
        raise AccessControl.Unauthorized("Go away, will you?")
    
    mapNonVocabularyTitles(getAllMembersWithNonVocabularyTitleByTitle(context))
