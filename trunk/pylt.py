#!/usr/bin/env python

#    Copyright (c) 2007 Corey Goldberg (corey@goldb.org)
#    License: GNU GPLv2
#
#    This file is part of PyLT.
#
#    PyLT is free software; you can redistribute it and/or modify it 
#    under the terms of the GNU General Public License as published 
#    by the Free Software Foundation; either version 2 of the License,
#    or (at your option) any later version.



from Tkinter import *
from threading import Thread
import xml.etree.ElementTree as etree
from pylt_engine import *

 

class Application:
    def __init__(self, root):
        self.root = root
        self.refresh_rate = 2
        self.runtime_stats = {}        
        self.init_gui()


    def init_gui(self):
        self.root.geometry('%dx%d%+d%+d' % (610, 350, 200, 100))
        mono_font = ('Courier', 8)
        small_font = ('Helvetica', 7)
        self.root.configure(background='#EFEFEF')
        self.root.title('PyLT - HTTP Load Test')

        #Label(self.root, text='TS Interval', background='#EFEFEF').place(x=15, y=115)
        #interval_entry = Entry(self.root, width=3)
        #interval_entry.place(x=78, y=115)
        #interval_entry.insert(0, '0')
        #self.interval_entry = interval_entry
        
        #Label(self.root, text='TS Interval', background='#EFEFEF').place(x=15, y=115)
        #interval_entry = Entry(self.root, width=3)
        #interval_entry.place(x=78, y=115)
        #interval_entry.insert(0, '0')
        #self.interval_entry = interval_entry
        
        self.btn_start = Button(self.root, text='Run', command=self.run, width=15)
        self.btn_start.place(x=15, y=70)
        
        self.btn_stop = Button(self.root, text='Stop', command=self.stop, width=15)
        self.btn_stop.place(x=15, y=96)
        self.btn_stop.configure(state=DISABLED)
        
        #Label(self.root, text='Run Num', background='#EFEFEF').place(x=15, y=140)
        #prefix_entry = Entry(self.root, width=6)
        #prefix_entry.place(x=78, y=140)
        #prefix_entry.insert(0, '')
        #self.prefix_entry = prefix_entry
               
        col_labels = 'Running Time            Requests                 Errors                      Avg Resp Time'
        Label(self.root, text=col_labels, background='#EFEFEF', font=small_font).place(x=128, y=34)
        txtbox_totals = Text(self.root, background='#CCCCCC', font=mono_font, width=50, height=1)
        txtbox_totals.place(x=130, y=50)
        self.txtbox_totals = txtbox_totals
        
        col_labels = 'Agent Num               Requests                 Last Resp Code        Last Resp Time        Avg Resp Time'
        Label(self.root, text=col_labels, background='#EFEFEF', font=small_font).place(x=128, y=84)
        txtbox_agents = Text(self.root, background='#CCCCCC', font=mono_font, width=65, height=16)
        txtbox_agents.place(x=130, y=100)
        self.txtbox_agents = txtbox_agents
        
        self.switch_status(False)

    
    def run(self):
        
        
        
        
            
        #lm = LoadManager(self.runtime_stats, 2, 3, 0)
        agents = 1
        lm = LoadManager(self.runtime_stats, agents, 0, 0)
        self.lm = lm
 
        cases, config = self.load_xml_cases()
        
        for req in cases:
            lm.add_req(req)
            
            
            
        
        lm.setDaemon(True)
        lm.start()
        
        c = Console(self.runtime_stats, self.refresh_rate, self.txtbox_agents, self.txtbox_totals)
        c.setDaemon(True)
        c.start()
        
        self.switch_status(True)
        
        
    def stop(self):
        self.lm.stop()
        self.switch_status(False)
        

    def load_xml_cases(self):
        # parse xml and load request queue
        dom = etree.parse('testcases.xml')
        cases = []
        for child in dom.getiterator():
            if child.tag != dom.getroot().tag and child.tag =='case':
                for element in child:
                    if element.tag == 'url':
                        req = Request()                
                        req.url = element.text
                    if element.tag == 'method': 
                        req.method = element.text
                    if element.tag == 'body': 
                        req.body = element.text
                    if element.tag == 'headers': 
                        req.headers = element.text
                cases.append(req)
            if child.tag != dom.getroot().tag and child.tag =='config':
                for element in child:
                    if element.tag == 'agents':
                        cfg = Config()                
                        cfg.agents = element.text
                    if element.tag == 'interval':
                        cfg.interval = element.text
                    if element.tag == 'rampup':
                        cfg.rampup = element.text
        return cases, cfg
                
        
    def switch_status(self, is_on):
        # flip the status light to gray or green and swap enabling of Start/Stop buttons
        if is_on:
            image = 'ui/greenlight.gif'
            self.btn_start.config(state='disabled')
            self.btn_stop.config(state='active')
        else:
            image = 'ui/graylight.gif'
            self.btn_start.config(state='active')
            self.btn_stop.config(state='disabled')
        try:
            self.canvas_statuslight.destroy()
        except:
            pass
        self.canvas_statuslight = Canvas(self.root, width=15, height=15, background='#EFEFEF', highlightthickness=0)
        self.canvas_statuslight.place(x=585, y=5)
        self.photo = PhotoImage(file=image)
        self.canvas_statuslight.create_image(0, 0, anchor=NW, image=self.photo)
        
        
        
        
class Console(Thread): # runs in its own thread so we don't block UI events      
    def __init__(self, runtime_stats, refresh_rate, txtbox_agents, txtbox_totals):
        Thread.__init__(self)
        self.runtime_stats = runtime_stats
        self.refresh_rate = refresh_rate
        self.txtbox_agents = txtbox_agents
        self.txtbox_totals = txtbox_totals
        
        
    def run(self):
        start_time = time.time()
        while True:
            self.txtbox_agents.delete(1.0, END)
            self.txtbox_totals.delete(1.0, END)
            for id in self.runtime_stats.keys():
                self.render_agentstats(id)
            self.render_totalstats(start_time)
            time.sleep(self.refresh_rate)


    def render_agentstats(self, id):
        col_width = 12
        col_separator = ' '
        self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, str(id + 1)))
        self.txtbox_agents.insert(INSERT, col_separator)
        self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, str(self.runtime_stats[id].count)))
        if self.runtime_stats[id].count > 0:                 
            self.txtbox_agents.insert(INSERT, col_separator)
            self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, str(self.runtime_stats[id].status)))
            self.txtbox_agents.insert(INSERT, col_separator)
            self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, '%.3f' % self.runtime_stats[id].latency))
            self.txtbox_agents.insert(INSERT, col_separator)
            self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, '%.3f' % self.runtime_stats[id].avg_latency))
        else:
            self.txtbox_agents.insert(INSERT, col_separator)
            self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, '-'))
            self.txtbox_agents.insert(INSERT, col_separator)
            self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, '-'))
            self.txtbox_agents.insert(INSERT, col_separator)
            self.txtbox_agents.insert(INSERT, self.pad_txt(col_width, '-'))            
        self.txtbox_agents.insert(INSERT, '\n')
        
        
    def render_totalstats(self, start_time):
        col_width = 12
        col_separator = ' '
        elapsed_secs = int(time.time() - start_time)  # running time in secs
        agg_count = sum([self.runtime_stats[id].count for id in self.runtime_stats.keys()])  # total req count
        agg_total = sum([self.runtime_stats[id].total_latency for id in self.runtime_stats.keys()])
        agg_count = sum([self.runtime_stats[id].count for id in self.runtime_stats.keys()])
        agg_error_count = sum([self.runtime_stats[id].error_count for id in self.runtime_stats.keys()])
        agg_avg = 0 # total avg response time
        if agg_count > 0:
            agg_avg = agg_total / agg_count
        self.txtbox_totals.insert(INSERT, self.pad_txt(col_width, '%d' % elapsed_secs))
        self.txtbox_totals.insert(INSERT, col_separator)
        self.txtbox_totals.insert(INSERT, self.pad_txt(col_width, '%d' % agg_count))
        self.txtbox_totals.insert(INSERT, col_separator)
        self.txtbox_totals.insert(INSERT, self.pad_txt(col_width, '%d' % agg_error_count))
        self.txtbox_totals.insert(INSERT, col_separator)
        self.txtbox_totals.insert(INSERT, self.pad_txt(col_width, '%.3f' % agg_avg))   
    
    
    def pad_txt(self, length, txt):
        pad_length = length - len(txt)
        padded_txt = txt
        padding = ''
        for i in range(pad_length):
            padding += ' '
        return txt + padding 
    


class Config():
    def __init__(self, agents=1, interval=1, rampup=0):
        self.agents = agents
        self.interval = interval
        self.rampup = rampup
            
            
            
def main():
    root = Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()
