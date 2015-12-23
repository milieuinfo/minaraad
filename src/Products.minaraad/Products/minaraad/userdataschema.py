from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.component.hooks import getSite
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder

from five import grok

from plone.app.users.userdataschema import IUserDataSchema
from plone.app.users.userdataschema import IUserDataSchemaProvider

from Products.CMFCore.utils import getToolByName

from quintagroup.formlib.captcha import Captcha

from Products.minaraad import MinaraadMessageFactory as _


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema


@grok.provider(IContextSourceBinder)
def gender_vocabulary(context):
    portal_memberdata = getToolByName(
        getSite(),
        'portal_memberdata')

    return SimpleVocabulary(
        [SimpleVocabulary.createTerm(x)
         for x in portal_memberdata.genders])


@grok.provider(IContextSourceBinder)
def country_vocabulary(context):
    portal_memberdata = getToolByName(
        getSite(),
        'portal_memberdata')

    return SimpleVocabulary(
        [SimpleVocabulary.createTerm(x)
         for x in portal_memberdata.select_country])


class IEnhancedUserDataSchema(IUserDataSchema):
    gender = schema.Choice(
        title=_(u'label_gender',
                default=u'Gender'),
        source=gender_vocabulary,
        required=False)

    firstname = schema.TextLine(
        title=_(u'label_firstname',
                default=u'First name'),
        required=True)

    company = schema.TextLine(
        title=_(u'label_company',
                default=u'Company'),
        required=False)

    jobtitle = schema.TextLine(
        title=_(u'label_jobtitle',
                default=u'Job title'),
        required=False)

    street = schema.TextLine(
        title=_(u'label_street',
                default=u'Street'),
        required=True)

    housenumber = schema.TextLine(
        title=_(u'label_housenumber',
                default=u'House number'),
        required=True)

    bus = schema.TextLine(
        title=_(u'label_bus',
                default=u'Bus'),
        required=False)

    zipcode = schema.TextLine(
        title=_(u'label_zipcode',
                default=u'Zipcode'),
        required=True)

    city = schema.TextLine(
        title=_(u'label_city',
                default=u'City'),
        required=True)

    country = schema.Choice(
        title=_(u'label_country',
                default=u'Country'),
        source=country_vocabulary,
        required=False,
    )

    other_country = schema.TextLine(
        title=_(u'label_other_country',
                default=u'Other country'),
        required=False,
    )

    phonenumber = schema.TextLine(
        title=_(u'label_phonenumber',
                default=u'Phone number'),
        required=False,
    )


class IRegisterForm(Interface):
    """ Marker interface for the custom register form.
    """


class ICaptchaSchema(Interface):
    captcha = Captcha(
        title=_(u'label_captcha',
                default=u'To block spammers, please solve this "captcha"'),
    )
