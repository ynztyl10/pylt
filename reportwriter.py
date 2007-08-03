#!/usr/bin/env python


import time



def write_starting_content(file_handle):
    file_handle.write('<h1>Pylot - Web Performance Results</h1>\n')
    file_handle.write('<p>Generated: %s</p>\n' % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime()))
    
    
def write_images(file_handle):
    file_handle.write('<h2>Response Time</h2>\n')
    file_handle.write('<img src="response_time_graph.png" alt="response time graph">\n')
    file_handle.write('<h2>Throughput</h2>\n')
    file_handle.write('<img src="throughput_graph.png" alt="throughput graph">\n')
    
    
def write_stats_tables(file_handle, stats_dict):
    file_handle.write('<p>%s: %d</p>\n' % ('Requests', stats_dict['response_count']))
    
    file_handle.write('<table>\n')
    file_handle.write('<th>Response Time</th><th>Throughput</th>\n')
    file_handle.write('<tr>\n')
    file_handle.write('<td>\n')
    
    file_handle.write('<table>\n')
    
    
    
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('avg', stats_dict['response_avg']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('stdev', stats_dict['response_stdev']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('min', stats_dict['response_min']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('max', stats_dict['response_max']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('50th %', stats_dict['response_50pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('80th %', stats_dict['response_80pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('90th %', stats_dict['response_90pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('95th %', stats_dict['response_95pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('99th %', stats_dict['response_99pct']))
    file_handle.write('</table>\n')
    file_handle.write('</td>\n')
    file_handle.write('<td>\n')
    file_handle.write('<table>\n')
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('avg', stats_dict['throughput_avg']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('stdev', stats_dict['throughput_stdev']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('min', stats_dict['throughput_min']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('max', stats_dict['throughput_max']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('50th %', stats_dict['throughput_50pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('80th %', stats_dict['throughput_80pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('90th %', stats_dict['throughput_90pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('95th %', stats_dict['throughput_95pct']))
    file_handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('99th %', stats_dict['throughput_99pct']))
    file_handle.write('</table>\n')
    file_handle.write('</td>\n')
    file_handle.write('</tr>\n')
    file_handle.write('</table>\n')
    

    
    
    
    
    

def write_head_html(file_handle):
    file_handle.write("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>Pylot - Results</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <meta http-equiv="Content-Language" content="en" />
    <style type="text/css">
        body {
            background-color: #FFFFFF;
            color: #000000;
            font-family: Trebuchet MS, Verdana, sans-serif;
            font-size: 11px;
            padding: 10px;
        }
        h1 {
            font-size: 16px;
            margin-bottom: 0.5em;
            background: #FF9933;
            padding-left: 5px;
            padding-top: 2px;
        }
        h2 {
            font-size: 12px;
            background: #C0C0C0;
            padding-left: 5px;
            margin-top: 2em;
            margin-bottom: .75em;
        }
        h3 {
            font-size: 11px;
            margin-bottom: 0.5em;
        }
        h4 {
            font-size: 11px;
            margin-bottom: 0.5em;
        }
        table {
            margin-bottom: 0;
        }
        td {
            text-align: right;
            color: #000000;
            background: #FFFFFF;
            padding-left: 10px;
            padding-bottom: 0px;
        }
        th {
            text-align: center;
            font-size: 12px;
            padding-right: 30px;
            padding-left: 30px;
            color: #000000;
            background: #C0C0C0;
        }
    </style>
</head>
<body>
""")
  
    

def write_closing_html(file_handle):
    file_handle.write("""\
</body>
</html>
    """)




