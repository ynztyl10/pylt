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


from pylab import *


def bar_graph(throughputs_dict, graph_title='', output_name='throughput_graph.png', xlabels=True):
    figure(figsize=(6, 2)) # image dimensions  
    title(graph_title, size='small')
    
    # add line
    plot(throughputs_dict.keys(), throughputs_dict.values(), color='blue', linestyle='-', linewidth=0.75)
            
    
#    # axis setup
#    xticks([]) # turn off axis labels
#    if xlabels:
#        xticks(arange(0.65, len(name_value_dict)),
#            [('%s: %d' % (name, value)) for name, value in
#            zip(name_value_dict.keys(), name_value_dict.values())], size='xx-small')
#    max_value = max(name_value_dict.values())
#    if max_value < 7:
#        step = 1
#    else:
#        step = max_value / 7        
#    tick_range = arange(0, max_value, step)
#    yticks(tick_range, size='xx-small')
#    formatter = FixedFormatter([str(x) for x in tick_range])
#    gca().yaxis.set_major_formatter(formatter)
#    gca().yaxis.grid(which='major')
   
    savefig(output_name) 
    