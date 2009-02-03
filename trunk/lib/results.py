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


import glob
import corestats
import graph
import reportwriter
import time
import pickle
from threading import Thread



def generate_results(dir, name):
    print 'Generating Results...'
    merged_log = merge_log_files(dir)
    merged_error_log = merge_error_files(dir)
    epoch_timings = list_timings(merged_log)
    
    # request throughput
    epochs = [int(x[0]) for x in epoch_timings] # grab just the epochs as rounded-down secs
    throughputs = calc_throughputs(epochs) # dict of secs and throughputs
    try:  # graphing only works on systems with Matplotlib installed
        graph.tp_graph(throughputs, dir=dir + '/')
    except: 
        print "ERROR: Unable to generate graphs with Matplotlib."
    throughput_stats = corestats.Stats(throughputs.values())

    # response times
    # subtract start times so we have resp times by elapsed time starting at zero
    start_epoch = epoch_timings[0][0]
    end_epoch = epoch_timings[-1][0]
    based_timings = [((epoch_timing[0] - start_epoch), epoch_timing[1]) for epoch_timing in epoch_timings] 
    try:  # graphing only works on systems with Matplotlib installed
        graph.resp_graph(based_timings, dir=dir + '/')
    except: 
        pass
    resp_data_set = [x[1] for x in epoch_timings] # grab just the timings
    response_stats = corestats.Stats(resp_data_set)
    
    # calc the stats and load up a dictionary with the results
    stats_dict = get_stats(response_stats, throughput_stats)
    
    # get the summary stats and load up a dictionary with the results   
    summary_dict = {}
    summary_dict['cur_time'] = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime())
    summary_dict['start_time'] = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(start_epoch))
    summary_dict['end_time'] = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(end_epoch))
    summary_dict['duration'] = int(end_epoch - start_epoch) + 1 # add 1 to round up
    summary_dict['num_agents'] =  len([psv_file for psv_file in glob.glob(dir + r'/*stats.psv')]) # count psv files to get number of agents that ran
    summary_dict['req_count'] = len(epochs)
    summary_dict['err_count'] = len(merged_error_log)
    summary_dict['bytes_received'] = calc_bytes(merged_log)
   
    # get the pickled stats dictionaries we saved
    runtime_stats_dict, workload_dict = load_dat_detail(dir)
    
    # write html report
    fh = open(dir + '/results.html', 'w')
    reportwriter.write_head_html(fh)
    reportwriter.write_starting_content(fh, name)
    reportwriter.write_summary_results(fh, summary_dict, workload_dict)
    reportwriter.write_stats_tables(fh, stats_dict)
    reportwriter.write_images(fh)
    reportwriter.write_agent_detail_table(fh, runtime_stats_dict)
    reportwriter.write_closing_html(fh)
    fh.close()

    print 'Results have been generated. You can view your test at:'
    print '%s/results.html\n' % dir


def load_dat_detail(dir):
    fh = open(dir + '/agent_detail.dat', 'r')
    runtime_stats = pickle.load(fh)
    fh.close()
    fh = open(dir + '/workload_detail.dat', 'r')
    workload = pickle.load(fh)
    fh.close()
    return (runtime_stats, workload)
        
    
def merge_log_files(dir):
    merged_file = []    
    for filename in glob.glob(dir + r'/*stats.psv'):
        fh = open(filename, 'rb')
        merged_file += fh.readlines()
        fh.close()
    return merged_file


def merge_error_files(dir):
    merged_file = []    
    for filename in glob.glob(dir + r'/*errors.log'):
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
        response_time = splat[-1].strip()
        epoch_timings.append((float(epoch), float(response_time)))
    epoch_timings.sort()
    return epoch_timings


def calc_bytes(merged_log):
    # get total bytes received
    bytes_seq = []
    for line in merged_log:
        bytes = int(line.split('|')[-2].strip())
        bytes_seq.append(bytes)
    total_bytes = sum(bytes_seq)
    return total_bytes
    

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
    

def get_stats(response_stats, throughput_stats):
    stats_dict = {}
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
    


class ResultsGenerator(Thread):  # generate results in a new thread so UI isn't blocked
    def __init__(self, dir, name):
        Thread.__init__(self)
        self.dir = dir
        self.test_name = name
        
    def run(self):
        try:
            generate_results(self.dir, self.test_name)
        except:
            print 'ERROR: Unable to generate results'
        
            
