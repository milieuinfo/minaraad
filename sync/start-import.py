import os, sys
import glob
from path import path

import zope.component

from tests.utils import setUpEnviron
setUpEnviron()

from CipraSync import interfaces
import minaraad.sync.configure

def main():
    minaraad.sync.configure.all()
    reader = zope.component.getUtility(interfaces.IReader)
    input_dir = path(__file__).parent / 'input'
    reader.feed(glob.glob(input_dir / '*'))
    writer = interfaces.IWriter(reader)
    writer.write()
    writer.commit()


if __name__ == '__main__':
    main()
