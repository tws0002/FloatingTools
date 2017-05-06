"""
FloatingTools is protected under the MIT license and is owned and maintained by Hatfield FX, LLC. 

Copyright (c) 2017 Hatfield FX, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# python imports
import os
import sys
import socket
import threading
import logging

logging.basicConfig(level=logging.INFO)

# namespace
__all__ = [
    'FLOATING_TOOLS_ROOT',
    'INSTALL_DIRECTORY',
    'PACKAGES',
    'PYTHON_EXECUTABLE',
    'DATA',
    'Dashboard',
    'Wrapper'
]

# Global variables
FT_LOOGER = logging.getLogger('FloatingTools')
FLOATING_TOOLS_ROOT = os.path.dirname(__file__)
INSTALL_DIRECTORY = os.path.dirname(FLOATING_TOOLS_ROOT)
PACKAGES = os.path.join(FLOATING_TOOLS_ROOT, 'packages')
DATA = os.path.join(FLOATING_TOOLS_ROOT, 'data')
WRAPPER = None
PYTHON_EXECUTABLE = sys.executable


try:
    # validate the install
    import install
    from install import releases, branches

    # dashboard import
    import Dashboard

    # add globals to dashboard
    Dashboard.setDashboardVariable('install_location', INSTALL_DIRECTORY)
    Dashboard.setDashboardVariable('python_location', PYTHON_EXECUTABLE)

    # handle wrapper
    from Wrapper import *

    # imports
    from settings import *

    # post install imports
    from connect import *
    from load import *

    # verify the login data.
    if verifyLogin() is False:
        Dashboard.login()

    # validate installed version of FloatingTools.
    install.loadVersion()

    # handle multi-threaded wrapper settings.
    if WRAPPER and WRAPPER.MULTI_THREAD or WRAPPER is None:
        threading.Thread(target=loadTools).start()
    else:
        print "Application does not support multi-threaded load up."
        loadTools()

except socket.gaierror:
    FT_LOOGER.error('No connection to Github could be established. Check your internet connection.')
