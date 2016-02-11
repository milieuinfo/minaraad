# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.minaraad import config
from Products.minaraad.content.MREvent import MREvent
from Products.minaraad.interfaces import IHearing
from zope.interface import implements


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
),
)

Hearing_schema = (
    atapi.BaseFolderSchema.copy() +
    getattr(MREvent, 'schema', atapi.Schema(())).copy() +
    schema.copy())

Hearing_schema.moveField('mot', after="description")


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
