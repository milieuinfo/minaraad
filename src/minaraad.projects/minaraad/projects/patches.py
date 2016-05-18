from archetypes.referencebrowserwidget.browser.view import \
    ReferenceBrowserPopup


REVERSED_SORTS = (
    'effective',
    'getObjPositionInParent',
    )


def getResult(self):
    # Default should be: order reversed on effective date.
    # So basically: make sure the most recently added item is shown first.
    # See MINA-136.
    form = self.request.form
    if not isinstance(self.widget.base_query, dict):
        self.widget.base_query = {}
    base_query = self.widget.base_query
    if 'sort_on' not in form:
        if 'sort_on' in base_query:
            form['sort_on'] = base_query['sort_on']
        else:
            form['sort_on'] = 'effective'
    # Set it on the base_query to, otherwise it may get overwritten in the
    # original getResult.
    sort_on = form['sort_on']
    if 'sort_on' not in base_query:
        base_query['sort_on'] = sort_on
    if sort_on in REVERSED_SORTS:
        if 'sort_order' not in form:
            form['sort_order'] = 'reverse'
    return self._getResult()


def apply_referencebrowser_patch():
    ReferenceBrowserPopup._getResult = ReferenceBrowserPopup.getResult
    ReferenceBrowserPopup.getResult = getResult


def unapply_referencebrowser_patch():
    ReferenceBrowserPopup.getResult = ReferenceBrowserPopup._getResult


def apply_all():
    apply_referencebrowser_patch()
