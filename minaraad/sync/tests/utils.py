import os, sys

def setUpEnviron():
    if os.environ.has_key('SOFTWARE_HOME'):
        sys.path.append(os.environ['SOFTWARE_HOME'])

    if os.environ.has_key('INSTANCE_HOME'):
        # Note that minaraad needs to be in 'import minaraad', therefore,
        # we want to append Products/ to PYTHONPATH
        sys.path.append(os.path.join(os.environ['INSTANCE_HOME'], 'Products'))

def tearDownEnviron():
    if os.environ.has_key('SOFTWARE_HOME'):
        sys.path.remove(os.environ['SOFTWARE_HOME'])

    if os.environ.has_key('INSTANCE_HOME'):
        # Note that minaraad needs to be in 'import minaraad', therefore,
        # we want to append Products/ to PYTHONPATH
        sys.path.remove(os.path.join(os.environ['INSTANCE_HOME'], 'Products'))
    
