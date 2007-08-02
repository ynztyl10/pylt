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


def resp_graph(nested_resp_list, graph_title='', dir='./', output_name='response_time_graph.png'):
    figure(figsize=(7, 2)) # image dimensions  
    title(graph_title, size='small')
    xticks(size='x-small')
    yticks(size='x-small')
    for i in range(len(nested_resp_list)):  # add bars
        bar(nested_resp_list[i][0], nested_resp_list[i][1], color='black')
    savefig(dir + output_name) 
    

def tp_graph(throughputs_dict, graph_title='', dir='./', output_name='throughput_graph.png'):
    figure(figsize=(7, 2)) # image dimensions  
    title(graph_title, size='small')
    xticks(size='x-small')
    yticks(size='x-small')
    for i, key in zip(range(len(throughputs_dict)), throughputs_dict.keys()):  # add bars
        bar(i, throughputs_dict[key], color='black')
    savefig(dir + output_name) 
    