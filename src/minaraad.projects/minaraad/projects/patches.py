from archetypes.referencebrowserwidget.browser.view import \
    ReferenceBrowserPopup

from Products.CMFPlone.PloneBatch import Batch


def getProjectResult(self):
    assert self._updated
    catalog = self.context.portal_catalog
    result = catalog(portal_type=self.allowed_types,
                     review_state=self.widget.only_for_review_states)

    b_size = int(self.request.get('b_size', 20))
    b_start = int(self.request.get('b_start', 0))

    return Batch(self._prepareResults(result), b_size, b_start, orphan=1)


def getResult(self):
    if self.widget.allow_browse:
        # Order reversed if we are ordering by position in parent.  So
        # basically: make sure the most recently added item is shown first.
        base_query = self.widget.base_query
        print(base_query)
        if isinstance(base_query, dict):
            default_sort = 'getObjPositionInParent'
            if base_query.get('sort_on', default_sort) == default_sort:
                self.request.form['sort_order'] = 'reverse'
        else:
            self.request.form['sort_order'] = 'reverse'
    if getattr(self, 'fieldName', '') == 'project':
        # Special handling for projects.
        return self.getProjectResult()
    # Standard handling for others.
    return self._getResult()


def apply_referencebrowser_patch():
    ReferenceBrowserPopup._getResult = ReferenceBrowserPopup.getResult
    ReferenceBrowserPopup.getProjectResult = getProjectResult
    ReferenceBrowserPopup.getResult = getResult


def unapply_referencebrowser_patch():
    ReferenceBrowserPopup.getResult = ReferenceBrowserPopup._getResult


def apply_all():
    apply_referencebrowser_patch()
