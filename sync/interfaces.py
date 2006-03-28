from zope import interface

class IDontWrite(interface.Interface):
    """A marker interface for values that shouldn't be written."""
    
    value = interface.Attribute("The actual value.")
