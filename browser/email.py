from Products.Five import BrowserView

class EmailOutView(BrowserView):
    
    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        
    def __call__(self):
        return self.index(template_id='email_out')
    
