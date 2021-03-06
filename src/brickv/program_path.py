# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2013 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>

program_path.py: Helper to figure out where the program is located

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation; either version 2 
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

# from http://www.py2exe.org/index.cgi/WhereAmI

import os
import sys

def get_program_path():
    if hasattr(sys, 'frozen'):
        path = sys.executable
    else:
        path = __file__

    return str(os.path.dirname(os.path.realpath(unicode(path, sys.getfilesystemencoding()))))
