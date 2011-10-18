from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from minaraad.projects import config
from minaraad.projects import MinaraadProjectMessageFactory as _
from minaraad.projects.interfaces import IOrganisation


organisation_schema = atapi.BaseSchema.copy() + atapi.Schema((
    atapi.StringField(
        name='address',
        widget=atapi.StringWidget(
            label=_(u'label_address',
                    default='Address'),
        ),
    ),

    atapi.StringField(
        name='postalCode',
        widget=atapi.StringWidget(
            label=_(u'label_postalCode',
                    default=u'Postalcode'),
        ),
    ),

    atapi.StringField(
        name='city',
        widget=atapi.StringWidget(
            label=_(u'label_city', default=u'City'),
            ),
        ),
    ))

organisation_schema['title'].widget.label = _(u'label_organisation_name',
                                              default=u'Name')


class Organisation(atapi.BaseContent):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (atapi.BaseContent.__implements__, )
    implements(IOrganisation)
    _at_rename_after_creation = True

    schema = organisation_schema

atapi.registerType(Organisation, config.PROJECTNAME)
