from Products.Five import BrowserView
from Products.PortalTransforms.utils import TransformException


class BaseHtmlView(BrowserView):
    """Show html view of ATFile"""

    def file_contents(self):
        """Return contents of the file, filefield or attachment"""
        pass  # Implement in subclass.

    def extract_html(self):
        """Return html for pdf/doc attachment"""
        # pt_tool = getToolByName(self.context, 'portal_transforms')
        pt_tool = self.context.portal_transforms
        # ^^^ getToolByName gives me a bogus unexisting one... [reinout]
        f = self.file_contents()
        if not f:
            return
        mt = f.getContentType()
        try:
            result = pt_tool.convertTo('text/html', str(f), mimetype=mt)
            if result:
                return result.getData()
        except TransformException:
            pass


class FileHtmlView(BaseHtmlView):
    """Show html view of ATFile"""

    def file_contents(self):
        """Return contents of the file"""
        return self.context.getFile()


class AttachmentHtmlView(FileHtmlView):
    """Show html view of AttachmentFile"""

    pass  # AttachmentFile is just a subclass of ATFile


class AttachmentFieldHtmlView(BaseHtmlView):
    """Show html view of ATFile"""

    def file_contents(self):
        """Return contents of the attachment field"""
        return self.context.getAttachment()
