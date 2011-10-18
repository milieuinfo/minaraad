from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class ContactPersonsListingView(BrowserView):
    """view displaying all contact persons.

    We just find them via the portal catalog.
    """

    def get_contact_persons(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(
            {'portal_type': 'ContactPerson',
             'sort_on': 'sortable_title'})
        return brains
