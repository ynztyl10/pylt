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


import glob
import corestats
import graph
import reportwriter



def generate_results(dir):
    merged_log = merge_log_files(dir)
    epoch_timings = list_timings(merged_log)
    
    # throughput
    epochs = [int(x[0]) for x in epoch_timings] # grab just the epochs as rounded-down secs
    throughputs = calc_throughputs(epochs) # dict of secs and throughputs
    graph.tp_graph(throughputs, dir=dir + '/')
    throughput_stats = corestats.Stats(throughputs.values())

    # response times
    # subtract start times so we have resp times by elapsed time starting at zero
    start_epoch = epoch_timings[0][0]
    based_timings = [((epoch_timing[0] - start_epoch), epoch_timing[1]) for epoch_timing in epoch_timings] 
    graph.resp_graph(based_timings, dir=dir + '/')
    resp_data_set = [x[1] for x in epoch_timings] # grab just the timings
    response_stats = corestats.Stats(resp_data_set)
    
    # calc the stats and load up a dictionary with the results
    stats_dict = calc_stats(response_stats, throughput_stats)
    print "calced stats"

    # write html report
    fh = open(dir + '/results.html', 'w')
    reportwriter.write_head_html(fh)
    reportwriter.write_starting_content(fh)
    reportwriter.write_stats_tables(fh, stats_dict)
    reportwriter.write_images(fh)
    reportwriter.write_closing_html(fh)
    fh.close()
    

    
def merge_log_files(dir):
    merged_file = []    
    for filename in glob.glob(dir + r'/*.psv'):
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
    
    
def calc_throughputs(epochs):
    # load up a dictionary with epochs as keys and counts as values   
    # need start and end times
    start_sec = epochs[0]
    end_sec = epochs[-1]
    throughputs = {}
    for epoch in range(start_sec, end_sec + 1):
        count = epochs.count(epoch)       
        throughputs[epoch - start_sec] = count
    return throughputs
    

def calc_stats(response_stats, throughput_stats):
    stats_dict = {}
    stats_dict['response_count'] = response_stats.count()
    stats_dict['response_avg'] = response_stats.avg()
    stats_dict['response_stdev'] = response_stats.stdev()
    stats_dict['response_min'] = response_stats.min()
    stats_dict['response_max'] = response_stats.max()
    stats_dict['response_50pct'] = response_stats.percentile(50)
    stats_dict['response_80pct'] = response_stats.percentile(80)
    stats_dict['response_90pct'] = response_stats.percentile(90)
    stats_dict['response_95pct'] = response_stats.percentile(95)
    stats_dict['response_99pct'] = response_stats.percentile(99)
    stats_dict['throughput_avg'] = throughput_stats.avg()
    stats_dict['throughput_stdev'] = throughput_stats.stdev()
    stats_dict['throughput_min'] = throughput_stats.min()
    stats_dict['throughput_max'] = throughput_stats.max()
    stats_dict['throughput_50pct'] = throughput_stats.percentile(50)
    stats_dict['throughput_80pct'] = throughput_stats.percentile(80)
    stats_dict['throughput_90pct'] = throughput_stats.percentile(90)
    stats_dict['throughput_95pct'] = throughput_stats.percentile(95)
    stats_dict['throughput_99pct'] = throughput_stats.percentile(99)
    return stats_dict 
    



    
    
    
    
    