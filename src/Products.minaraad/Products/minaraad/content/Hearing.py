# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from zope.interface import Interface
from zope.interface import implements

from Products.minaraad import config
from Products.minaraad.EmailMixin import EmailMixin
from Products.minaraad.content.MREvent import MREvent


schema = atapi.Schema((

    atapi.BooleanField(
        name='mot',
        widget=atapi.BooleanWidget(
            description="Check this option if the hearing is a MOT.",
            label='Mot',
            label_msgid='minaraad_label_mot',
            description_msgid='minaraad_help_mot',
            i18n_domain='minaraad',
        )
    ),
    atapi.BooleanField(
        name='subscriptionAllowed',
        default=True,
        widget=atapi.BooleanWidget(
            label='Subscription allowed',
            label_msgid='minaraad_label_subscription_allowed',
            description='By default, subscription is allowed till one day before start of the event. Uncheck this field to disallow subscription immediately.',
            description_msgid='minaraad_description_subscription_allowed',
            i18n_domain='minaraad',
        ),
    ),
),
)

Hearing_schema = (
    atapi.BaseFolderSchema.copy() +
    getattr(MREvent, 'schema', atapi.Schema(())).copy() +
    schema.copy())

Hearing_schema.moveField('theme', after="goal")
Hearing_schema.moveField('email_themes', after="theme")
Hearing_schema.moveField('mot', after="email_themes")


class IHearing(Interface):
    """Marker interface for hearings"""
    pass


class Hearing(MREvent, atapi.BaseFolder):
    """
    A Hearing
    """
    security = ClassSecurityInfo()
    implements(IHearing)

    # This name appears in the 'add' box
    archetype_name = 'Hearing'

    meta_type = 'Hearing'
    portal_type = 'Hearing'
    allowed_content_types = (
        list(getattr(MREvent, 'allowed_content_types', [])) +
        list(getattr(EmailMixin, 'allowed_content_types', [])))
    filter_content_types = 1
    global_allow = 1
    #content_icon = 'Hearing.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Hearing"
    typeDescMsgId = 'description_edit_hearing'

    _at_rename_after_creation = True
    schema = Hearing_schema


atapi.registerType(Hearing, config.PROJECTNAME)
