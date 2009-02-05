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
  -o, --output=PATH           :  output directory
  -n, --name=TESTNAME	      :  name of test
  -l, --log_responses         :  log responses
  -g, --gui                   :  start GUI  
"""

VERSION = '1.20'

import sys
import lib.optionparse as optionparse


# default parameters
agents = 1
duration = 60  # secs
rampup = 0  # secs
interval = 0  # millisecs
tc_xml_filename = 'testcases.xml'
log_responses = False
output = None
test_name = None
gui = False


# parse command line arguments
opt, args = optionparse.parse(__doc__)

if not opt and not args:
    print 'version: ' + VERSION
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
    if opt.output:
        output = opt.output
    if opt.name:
        test_name = opt.name
    if opt.gui:
        gui = True
except:
   print 'Invalid Argument'
   sys.exit(1)


if gui:  # gui mode
    import lib.pylot_gui as pylot_gui
    pylot_gui.main(agents, rampup, interval, duration, tc_xml_filename, log_responses, VERSION, output, test_name)
    
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
    if output:
        print '  output location:           %s' % output
    print '\n'
    try:    
        pylot_shell.start(agents, rampup, interval, duration, tc_xml_filename, log_responses, output, test_name)
    except KeyboardInterrupt:
        print '\nInterrupt'
        sys.exit(1)

