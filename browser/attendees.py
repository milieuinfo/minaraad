from Products.Five import BrowserView

class AttendeesManagerView(BrowserView):
    
    def __call__(self):
        return self.index(template_id='attendees')
