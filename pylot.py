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
  -a, --agents=NUM_AGENTS  :  number of agents
  -r, --rampup=RAMPUP      :  rampup in seconds
  -i, --interval=INTERVAL  :  interval in milliseconds
  -d, --duration=DURATION  :  test duration in seconds
  -l, --log_responses      :  log responses
  -g, --gui                :  start GUI
  -o, --output=PATH        :  specify output
  -n, --name=TESTNAME	   :  specify name of test  
"""

VERSION = '1.12'

import sys
import lib.optionparse as optionparse


# default parameters
agents = 1
rampup = 0
interval = 0
duration = 60
log_responses = False
gui = False
output = None
name = None


# parse command line arguments
opt, args = optionparse.parse(__doc__)

if not opt and not args:
    print 'version: ' + VERSION
    optionparse.exit()
try:
    if opt.agents:
        agents = int(opt.agents)
    if opt.rampup:
        rampup = int(opt.rampup)
    if opt.interval:
        interval =  int(opt.interval)
    if opt.duration:
        duration = int(opt.duration)
    if opt.log_responses: 
        log_responses = True
    if opt.gui:
        gui = True
    if opt.output:
        output = opt.output
    if opt.name:
        name = opt.name
except:
   print 'Invalid Argument'
   sys.exit(1)


if gui:  # gui mode
    import lib.pylot_gui as pylot_gui
    pylot_gui.main(agents, rampup, interval, duration, log_responses, VERSION, output, name)
    
else:  # shell/console mode 
    import lib.pylot_shell as pylot_shell
    print '\n-------------------------------------------------'
    print 'Test parameters:'
    print '  number of agents:          %s' % agents
    print '  rampup in seconds:         %s' % rampup
    print '  interval in milliseconds:  %s' % interval
    print '  test duration in seconds:  %s' % duration
    print '  log responses:             %s' % log_responses
    print '\n'
    try:    
        pylot_shell.start(agents, rampup, interval, duration, log_responses, output, name)
    except KeyboardInterrupt:
        print '\nInterrupt'
