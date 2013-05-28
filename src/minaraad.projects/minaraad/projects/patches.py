from archetypes.referencebrowserwidget.browser.view import ReferenceBrowserPopup

from Products.CMFPlone.PloneBatch import Batch


def getProjectResult(self):
    assert self._updated
    catalog = self.context.portal_catalog
    result = catalog(portal_type=self.allowed_types,
                     review_state=self.widget.only_for_review_states)

    b_size = int(self.request.get('b_size', 20))
    b_start = int(self.request.get('b_start', 0))

    return Batch(result, b_size, b_start, orphan=1)


def getResult(self):
    if getattr(self, 'fieldName', '') == 'project':
        return self.getProjectResult()
    return self._getResult()


def apply_referencebrowser_patch():
    ReferenceBrowserPopup._getResult = ReferenceBrowserPopup.getResult
    ReferenceBrowserPopup.getProjectResult = getProjectResult
    ReferenceBrowserPopup.getResult = getResult


def unapply_referencebrowser_patch():
    ReferenceBrowserPopup.getResult = ReferenceBrowserPopup._getResult


def apply_all():
    apply_referencebrowser_patch()
