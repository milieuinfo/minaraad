from archetypes.referencebrowserwidget.browser.view import \
    ReferenceBrowserPopup


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
    return self._getResult()


def apply_referencebrowser_patch():
    ReferenceBrowserPopup._getResult = ReferenceBrowserPopup.getResult
    ReferenceBrowserPopup.getResult = getResult


def unapply_referencebrowser_patch():
    ReferenceBrowserPopup.getResult = ReferenceBrowserPopup._getResult


def apply_all():
    apply_referencebrowser_patch()
