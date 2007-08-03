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


from pylab import *  # Matplotlib



# response time graph
def resp_graph(nested_resp_list, graph_title='', dir='./', output_name='response_time_graph.png'):
    fig = figure(figsize=(8, 3))  # image dimensions  
    ax = fig.add_subplot(111)
    ax.set_xlabel('Elapsed Time In Test (sec)', size='x-small')
    ax.set_ylabel('Response Time (sec)' , size='x-small')
    ax.grid(True, color='#666666')
    xticks(size='x-small')
    yticks(size='x-small')
    x_seq = [item[0] for item in nested_resp_list] 
    y_seq = [item[1] for item in nested_resp_list] 
    ax.plot(x_seq, y_seq, color='blue', linestyle='-', linewidth=1.0, marker='o', markeredgecolor='blue', markerfacecolor='yellow', markersize=2.0)
    savefig(dir + output_name) 
    
    

# throughput graph
def tp_graph(throughputs_dict, graph_title='', dir='./', output_name='throughput_graph.png'):
    fig = figure(figsize=(8, 3))  # image dimensions  
    ax = fig.add_subplot(111)
    ax.set_xlabel('Elapsed Time In Test (sec)', size='x-small')
    ax.set_ylabel('Requests Per Second (count)' , size='x-small')
    ax.grid(True, color='#666666')
    xticks(size='x-small')
    yticks(size='x-small')
    keys = throughputs_dict.keys()
    keys.sort()
    values = []
    for key in keys:
        values.append(throughputs_dict[key])
    x_seq = keys
    y_seq = values
    ax.plot(x_seq, y_seq, color='red', linestyle='-', linewidth=1.0, marker='o', markeredgecolor='red', markerfacecolor='yellow', markersize=2.0)
    savefig(dir + output_name) 
    