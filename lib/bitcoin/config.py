# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Utilities for reading bitcoin configuration files.
"""
def read_config_file(filename):
    """
    Read a simple ``'='``-delimited config file.
    Raises :const:`IOError` if unable to open file, or :const:`ValueError`
    if an parse error occurs.
    """
    f = open(filename)
    try:
        cfg = {}
        for line in f:
	    line = line.rstrip()
	    if line:
	        (key, value) = line.split('=', 1)
	        cfg[key] = value
    finally:
        f.close()
    return cfg

def read_default_config():
    """
    Read bitcoin default configuration from the current user's home directory.
    """
    import os
    home = os.getenv("HOME")
    if not home:
        raise IOError("Home directory not defined, don't know where to look for config file")
     
    try:
        return read_config_file(os.path.join(home, '.bitcoin/bitcoin.conf'))
    except (IOError,ValueError):
        pass # Cannot read config file, ignore


