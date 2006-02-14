from Testing.ZopeTestCase import PortalTestCase

PATCH_PREFIX = '_monkey_'

__refresh_module__ = 0


def monkeyPatch(originalClass, patchingClass):
    #print 'monkeyPatch', originalClass.__name__, patchingClass.__name__
    """Monkey patch original class with attributes from new class
       (Swiped from SpeedPack -- thanks, Christian Heimes!)
    
    * Takes all attributes and methods except __doc__ and __module__ from patching class
    * Safes original attributes as _monkey_name
    * Overwrites/adds these attributes in original class
    """
    for name, newAttr in patchingClass.__dict__.items():
        # don't overwrite doc or module informations
        if name not in ('__doc__', '__module__'):
            # safe the old attribute as __monkey_name if exists
            # __dict__ doesn't show inherited attributes :/
            orig = getattr(originalClass, name, None)
            if orig:
                stored_orig_name = PATCH_PREFIX + name
                stored_orig = getattr(originalClass, stored_orig_name, None)
                # don't double-patch on refresh!
                if stored_orig is None:
                    setattr(originalClass, stored_orig_name, orig)
            # overwrite or add the new attribute
            setattr(originalClass, name, newAttr)


class PatchedPortalTestCase:
    
    def _setupHomeFolder(self):
        """Creates the default user's home folder.
        """

        try:
            self.createMemberarea(user_name)
            pm = self.portal.portal_membership
            self.folder = pm.getHomeFolder(user_name)
        except:
            pass

# handle zopetestcase

monkeyPatch(PortalTestCase, PatchedPortalTestCase)
