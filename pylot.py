#!/usr/bin/env python
#
#    Copyright (c) 2007-2009 Corey Goldberg (corey@goldb.org)
#    License: GNU GPLv3
#
#    This file is part of Pylot.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License 
#    for more details.
#


"""
  usage: %prog [options] args
  -a, --agents=NUM_AGENTS     :  number of agents
  -d, --duration=DURATION     :  test duration in seconds
  -r, --rampup=RAMPUP         :  rampup in seconds
  -i, --interval=INTERVAL     :  interval in milliseconds
  -x, --xmlfile=TEST_CASE_XML :  test case xml file
  -o, --output_dir=PATH       :  output directory
  -n, --name=TESTNAME	      :  name of test
  -l, --log_responses         :  log responses
  -b, --blocking              :  blocking mode
  -g, --gui                   :  start GUI  
"""

VERSION = '1.21'

import sys
import lib.optionparse as optionparse


# default parameters
agents = 1
duration = 60  # secs
rampup = 0  # secs
interval = 0  # millisecs
tc_xml_filename = 'testcases.xml'
log_responses = False
output_dir = None
test_name = None
blocking = False
gui = False


# parse command line arguments
opt, args = optionparse.parse(__doc__)

if not opt and not args:
    print 'version: %s' % VERSION
    optionparse.exit()
try:
    if opt.agents:
        agents = int(opt.agents)
    if opt.duration:
        duration = int(opt.duration)
    if opt.rampup:
        rampup = int(opt.rampup)
    if opt.interval:
        interval = int(opt.interval)
    if opt.xmlfile:
        tc_xml_filename = opt.xmlfile
    if opt.log_responses: 
        log_responses = True
    if opt.output_dir:
        output_dir = opt.output_dir
    if opt.name:
        test_name = opt.name
    if opt.blocking:
        blocking = True
    if opt.gui:
        gui = True
except Exception, e:
   print 'Invalid Argument'
   sys.exit(1)


if gui:  # gui mode
    import lib.pylot_gui as pylot_gui
    pylot_gui.main(agents, rampup, interval, duration, tc_xml_filename, log_responses, VERSION, output_dir, test_name)


elif blocking:  # blocked output mode (stdout blocked until test finishes, then result is returned)
    import lib.pylot_blocking as pylot_blocking
    try:    
        pylot_blocking.start(agents, rampup, interval, duration, tc_xml_filename, log_responses, output_dir, test_name)
    except KeyboardInterrupt:
        print '\nInterrupt'
        sys.exit(1)
        
        
else:  # shell/console mode
    import lib.pylot_shell as pylot_shell
    print '\n-------------------------------------------------'
    print 'Test parameters:'
    print '  number of agents:          %s' % agents
    print '  test duration in seconds:  %s' % duration
    print '  rampup in seconds:         %s' % rampup
    print '  interval in milliseconds:  %s' % interval
    print '  test case xml:             %s' % tc_xml_filename
    print '  log responses:             %s' % log_responses
    if test_name:
        print '  test name:                 %s' % test_name
    if output_dir:
        print '  output directory:           %s' % output_dir
    print '\n'
    try:    
        pylot_shell.start(agents, rampup, interval, duration, tc_xml_filename, log_responses, output_dir, test_name)
    except KeyboardInterrupt:
        print '\nInterrupt'
        sys.exit(1)
    


