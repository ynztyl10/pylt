#!/usr/bin/env python
#
#    Copyright (c) 2007 Corey Goldberg (corey@goldb.org)
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


import corestats
import glob


def generate_results(dir):
    merged_log = merge_log_files(dir)
    epoch_timings = list_timings(merged_log)
    
    # grab just the timings
    data_set = [x[1] for x in epoch_timings]  
    
    stats = corestats.Stats(data_set)
    
    print 'count:', stats.count()
    print 'avg:', stats.avg()
    print 'stdev:', stats.stdev()
    print 'min:', stats.min()
    print 'max:', stats.max()
    print '80 pct:', stats.percentile(80)
    print '90 pct:', stats.percentile(90)
    print '95 pct:', stats.percentile(95)
    print '99 pct:', stats.percentile(99)
    
    
    #for foo in epoch_timings:
    #    print foo
    
    
    
def merge_log_files(dir):
    merged_file = []    
    for filename in glob.glob(dir + r'\*'):
        fh = open(filename, 'rb')
        merged_file += fh.readlines()
        fh.close()
    return merged_file



def list_timings(merged_log):
    # create a list of tuples with our timing data sorted by epoch
    epoch_timings = []
    for line in merged_log:
        splat = line.split('|')
        epoch = splat[2].strip()
        response_time = splat[6].strip()
        epoch_timings.append((float(epoch), float(response_time)))
    epoch_timings.sort()
    return epoch_timings
    
    
