from webkit2png import WebkitRenderer

import sys
import signal
import os
import urlparse
from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

class Html2Png:
    def __init__(self):
       #self.app_gui = self.init_qtgui()
       self.renderer = WebkitRenderer()
       self.renderer.format = 'jpg'
       self.renderer.width = 1024
       self.renderer.height = 900
       #pass               

    def init_qtgui(display=None, style=None, qtargs=None):
        """Initiates the QApplication environment using the given args."""
        if QApplication.instance():
            logger.debug("QApplication has already been instantiated. \
                            Ignoring given arguments and returning existing QApplication.")
            return QApplication.instance()

        qtargs2 = [sys.argv[0]]
        if display:
            qtargs2.append('-display')
            qtargs2.append(display)
            # Also export DISPLAY var as this may be used
            # by flash plugin
            os.environ["DISPLAY"] = display

        if style:
            qtargs2.append('-style')
            qtargs2.append(style)

        qtargs2.extend(qtargs or [])
        return QApplication(qtargs2)    
	
    def init_qtgui_deprecated(display=None, style=None, qtargs=None):
       """Initiates the QApplication environment using the given args."""
       if QApplication.instance():
          return QApplication.instance()

       qtargs2 = [sys.argv[0]]

       if display:
          qtargs2.append('-display')
          qtargs2.append(display)
          # Also export DISPLAY var as this may be used
          # by flash plugin
          os.environ["DISPLAY"] = display

       if style:
          qtargs2.append('-style')
          qtargs2.append(style)

       qtargs2.extend(qtargs or [])

       return QApplication(qtargs2)
       
    def goHtml2Png(self, content, fname):
       f = open("/tmp/%s.html" % (fname),"w") 
       f.write(content)
       f.close()     
       
       #self.renderer = WebkitRenderer()
       #self.renderer.format = 'jpg'
       #self.renderer.width = 1024
       #self.renderer.height = 768        
       original_filepath = "/tmp/%s.jpg" % (fname)
       original_file = open(original_filepath, "w")
       self.renderer.render_to_file("file:///tmp/%s.html" % (fname), original_file)
       #self.renderer.render_to_file("file:///tmp/62811987905_order_22335269.html", original_file)       
       original_file.close()          