import logging
from Acquisition import aq_inner
from Products.Five import BrowserView

logger = logging.getLogger('configlets')


LONGDESC = {
    21: ('Europese, Belgische, Vlaamse regelgeving &amp; planning, '
         'duurzame ontwikkeling, begroting'),
    22: 'Heffingen, steun, handhaving, vergunningen, m.e.r.',
    23: 'Lucht, bodem, afval, energie',
    # Nothing for 24
    25: 'Landbouw, natuur, bos, jacht, erkenningen',
    # Nothing for 26
    27: 'NME, samenwerkingsovereenkomst',
}


class AbstractView(BrowserView):

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self._buildReferral()

    def _buildReferral(self):
        context = aq_inner(self.context)
        self.referring_url = (self.request.get('referring_url', None) or
                              self.request.get('HTTP_REFERER', None) or
                              context.absolute_url())
        pos = self.referring_url.find('?')
        if pos > -1:
            self.referring_url = self.referring_url[:pos]
