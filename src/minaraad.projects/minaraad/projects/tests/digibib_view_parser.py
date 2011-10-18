from HTMLParser import HTMLParser


class DigiBibHtmlParser(HTMLParser):
    """ Collects all <a> tags
    """

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.path = []
        self.in_view = False
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        tag_id = attrs.get('id', '')
        self.path.append({'tag': tag, 'id': tag_id})

        if tag == 'div':
            if tag_id == 'digibib_view':
                self.in_view = True

        if tag == 'a' and self.in_view:
            self.links.append(attrs.get('href', None))

    def handle_endtag(self, tag):
        if not self.path:
            return

        t = self.path.pop()
        tag_id = t.get('id', '')
        # tag_classes = t.get('class', '')

        if tag_id == 'digibib_view':
            self.in_view = False
