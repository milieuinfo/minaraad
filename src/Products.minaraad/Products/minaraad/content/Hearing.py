# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from zope.interface import Interface
from zope.interface import implements

from Products.minaraad import config
from Products.minaraad.interfaces import IHearing
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


class Hearing(MREvent, atapi.BaseFolder):
    """
    A Hearing
    """
    security = ClassSecurityInfo()
    implements(IHearing)
    archetype_name = 'Hearing'
    portal_type = 'Hearing'
    _at_rename_after_creation = True
    schema = Hearing_schema


atapi.registerType(Hearing, config.PROJECTNAME)
