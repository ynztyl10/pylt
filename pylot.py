#!/usr/bin/env python
#
#    Copyright (c) 2007-2008 Corey Goldberg (corey@goldb.org)
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
  -a, --agents=NUM_AGENTS:   number of agents
  -r, --rampup=RAMPUP:       rampup in seconds
  -i, --interval=INTERVAL:   interval in miliseconds
  -d, --duration=DURATION:   test duration in seconds
  -l, --logresp:             log responses
  -g, --gui:                 start GUI
"""

import optionparse


# default parameters
agents = 1
rampup =0
interval = 1000
duration = 60
logresp = False
gui = False


# parse the commad line arguments
# in case of wrong arguments quit and print the usage message
opt, args = optionparse.parse(__doc__)
if not opt and not args:
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
    if opt.logresp: 
        logresp = True
    if opt.gui:
        gui=True
except:
    optionparse.exit()

if gui:  # when user tries to start gui
    try:
        import pylot_gui
        pylot_gui.main(agents, rampup, interval, duration, logresp)
    except:
        sys.stderr.write('Pylot was not able to start the GUI, check if wxPython is installed properly.')
        sys.exit(1)
else:  # when it's started in console mode 
    import pylot_shell
    pylot_shell.start(agents, rampup, interval, duration, logresp)