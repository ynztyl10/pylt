#!/usr/bin/env python
#
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


import sys
import time
import xmlparse
from threading import Thread
from pylot_engine import LoadManager



# flag is set if the script is run on windows
is_windows = sys.platform.startswith('win')
#the _cpos c++ extension defines windows native functions
#for positioning the cursor in the command prompt
#since ANSI sequence support is disabled by default
#on windows, more info: http://en.wikipedia.org/wiki/ANSI_escape_code

#The _cpos.pyd file is just a renamed dll.  See the c++ source code
#the library, it's built with Visual Studio, you can
#distribute it with the whole app but also include the pyd file, so
#users don't need to install VS or mingw and go through the pain of
#building it.



if is_windows: import _cpos

class ProgressBar:
    def __init__(self, duration, min_value=0, max_value=100, total_width=40):
        self.prog_bar = '[]'  # holds the progress bar string
        self.duration = duration
        self.min = min_value
        self.max = max_value
        self.span = max_value - min_value
        self.width = total_width
        self.amount = 0  # when amount == max, we are 100% done
        self.update_amount(0)  # build progress bar string
    
    
    def update_amount(self, new_amount=0):
        if new_amount < self.min: new_amount = self.min
        if new_amount > self.max: new_amount = self.max
        self.amount = new_amount
        
        # figure out the new percent done, round to an integer
        diff_from_min = float(self.amount - self.min)
        percent_done = (diff_from_min / float(self.span)) * 100.0
        percent_done = round(percent_done)
        percent_done = int(percent_done)
        
        # figure out how many hash bars the percentage should be
        all_full = self.width - 2
        num_hashes = (percent_done / 100.0) * all_full
        num_hashes = int(round(num_hashes))
        
        # build a progress bar with hashes and spaces
        self.prog_bar = '[' + '#' * num_hashes + ' ' * (all_full - num_hashes) + ']'
        
        # figure out where to put the percentage, roughly centered
        percent_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        percent_string = str(percent_done) + '%'

        # slice the percentage into the bar
        self.prog_bar = self.prog_bar[0:percent_place] + (percent_string + self.prog_bar[percent_place + len(percent_string):])
                    
    
    def update_time(self, elapsed_secs):

        self.update_amount((elapsed_secs / self.duration) * 100)
        self.prog_bar += '  %ds/%ss' % (elapsed_secs, self.duration)
        
        
    def __str__(self):
        return str(self.prog_bar)



class RuntimeReporter(object):
    def __init__(self, duration, runtime_stats):
        self.runtime_stats = runtime_stats
        self.progress_bar = ProgressBar(duration)
        self.last_count = 0  # requests since last refresh
        self.refreshed_once = False  #j ust to know if we should move the cursor up
        
        
    def move_up(self, times):
        for i in range(times):
            if is_windows:
                x,y = _cpos.getpos()
                _cpos.gotoxy(0, y-1)
            else:
                ESC = chr(27) #E scape key
                sys.stdout.write(ESC + '[G' )
                sys.stdout.write(ESC + '[A' )
            
            
    def refresh(self, elapsed_secs, refresh_rate):
        ids = self.runtime_stats.keys()

        agg_count = sum([self.runtime_stats[id].count for id in ids])  # total req count
        agg_total_latency = sum([self.runtime_stats[id].total_latency for id in ids])
        agg_error_count = sum([self.runtime_stats[id].error_count for id in ids])
        if agg_count > 0 and elapsed_secs > 0:
            agg_avg = agg_total_latency / agg_count  # total avg response time
            avg_throughput = float(agg_count) / elapsed_secs  # avg throughput since start
            
            interval_count = agg_count - self.last_count 
            cur_throughput = float(interval_count) / refresh_rate  # throughput since last refresh
            self.last_count = agg_count  # reset for next time
        
            if self.refreshed_once:
                #move the cursor up 6 times
                self.move_up(6)
            self.progress_bar.update_time(elapsed_secs)    
            print self.progress_bar
            print 'Requests: %d\nAvg. Response Time: %.3f\nErrors: %d\nAvg. Throughput: %.2f\nCur. Throughput: %d' % (
                agg_count, agg_avg, agg_error_count, avg_throughput, cur_throughput)        
            self.refreshed_once = True
        

def start(num_agents, rampup, interval, duration, log_resps):
    runtime_stats = {}
    error_queue = []
    interval = interval / 1000.0  # convert from millisecs to secs
    
    # create a load manager
    lm = LoadManager(num_agents, interval, rampup, log_resps, runtime_stats, error_queue)
    
    # load the test cases
    try:
        cases = xmlparse.load_xml_cases()
        for req in cases:
            lm.add_req(req)
    except:  # if there was a problem getting cases from the xml file
        sys.stderr.write('Error opening testcase file.\n')
        sys.exit(1)
    
    start_time = time.time()
    
    # start the load manager
    lm.setDaemon(True)
    lm.start()
    
    reporter = RuntimeReporter(duration, runtime_stats)
    while (time.time() < start_time + duration):         
        refresh_rate = 1.0
        time.sleep(refresh_rate)
        
        # when all agents are started start displaying the progress bar and stats
        if lm.agents_started:
            elapsed_secs = time.time() - start_time
            reporter.refresh(elapsed_secs, refresh_rate)

    sys.stdout.write('\n')
    lm.stop()
    print 'Generating results...'
    # wait until the result generator is finished
    while lm.results_gen.isAlive():
        time.sleep(.05)
    print 'Done.'
    
