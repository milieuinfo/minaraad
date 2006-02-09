# File: Themes.py
#
# Copyright (c) 2006 by Zest Software
# Generator: ArchGenXML Version 1.4.1 svn/devel
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

from Products.CMFCore.utils import UniqueObject

    
##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Themes_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Themes(UniqueObject,BaseContent):
    security = ClassSecurityInfo()
    __implements__ = (getattr(UniqueObject,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name = 'Themes'

    meta_type = 'Themes'
    portal_type = 'Themes'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = False
    #content_icon = 'Themes.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Themes"
    typeDescMsgId = 'description_edit_themes'
    #toolicon = 'Themes.gif'

    schema = Themes_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        BaseContent.__init__(self,'portal_themes')
        
        ##code-section constructor-footer #fill in your manual code here
        ##/code-section constructor-footer



    # Methods
    # Manually created methods

    security.declareProtected('View', "getThemesList")
    def getThemesList(self):
        themes_list = ['Alles', 'Water', 'Klimaat & energie', 'Afval', 
        'Bodem', 'Europa & Duurzame ontwikkeling', 'Mobiliteit', 
        'Ruimtelijke ordening', 'Natuur & landbouw', 'NME', 'Milieubegroting', 
        'Milieuplanning', 'Milieureglementering', 'Instrumenten',]
        try:
            return self.themes
        except AttributeError:
            self.themes = themes_list
            return self.themes
    

    def configure_themes(self, themes, REQUEST=None, 
        installBeforeUnload=None):
        """Delete resource types through the ZMI"""
        
        if installBeforeUnload is not None:
            self.install_beforeunload = bool(installBeforeUnload)
            
        self.themes = list(themes)
        
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/themes_config')



registerType(Themes,PROJECTNAME)
# end of class Themes

##code-section module-footer #fill in your manual code here
##/code-section module-footer



