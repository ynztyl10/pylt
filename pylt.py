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



import time
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from threading import Thread
import xml.etree.ElementTree as etree
from pylt_engine import *

 

    
class Application(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'PyLT - Web Performance', size=(780, 600))
        
        self.runtime_stats = {}
        
        #text = wx.StaticText(panel, -1, "PyLT - Web Performance")
        #text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        #text.SetSize(text.GetBestSize())
        
        panel = wx.Panel(self)
        
        self.run_btn = wx.Button(panel, -1, 'Run')
        self.stop_btn = wx.Button(panel, -1, 'Stop')
        
        self.busy_gauge = wx.Gauge(panel, -1, 50, size=(100, 10))
        self.busy_timer = wx.Timer(self)
        
        
        
        

        self.total_statlist = AutoWidthListCtrl(panel)
        self.total_statlist.InsertColumn(0, 'Run Time', width=100)
        self.total_statlist.InsertColumn(1, 'Requests', width=100)
        self.total_statlist.InsertColumn(2, 'Errors', width=100)
        self.total_statlist.InsertColumn(3, 'Avg Resp Time', width=100)
        
        self.agents_statlist = AutoWidthListCtrl(panel)
        self.agents_statlist.InsertColumn(0, 'Agent Num', width=100)
        self.agents_statlist.InsertColumn(1, 'Requests', width=100)
        self.agents_statlist.InsertColumn(2, 'Last Resp Code', width=100)
        self.agents_statlist.InsertColumn(3, 'Last Resp Time', width=100)
        self.agents_statlist.InsertColumn(4, 'Avg Resp Time', width=100)
                
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.total_statlist, 0, wx.EXPAND, 0)
        sizer.Add(self.agents_statlist, 0, wx.EXPAND, 0)
        sizer.Add(self.run_btn, 0, wx.ALL, 3)
        sizer.Add(self.stop_btn, 0, wx.ALL, 3)
        sizer.Add(self.busy_gauge, 0, wx.ALL, 3)
        
        
        panel.SetSizer(sizer)
        
        
        
        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.on_run, self.run_btn)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_btn)
        self.Bind(wx.EVT_TIMER, self.timer_handler)
        
        
        
        self.Centre()
        self.Show(True)
                
        self.switch_status(False)

    
    def timer_handler(self, evt):
        self.busy_gauge.Pulse()
        
        
    def on_run(self, evt):
        #lm = LoadManager(self.runtime_stats, 2, 3, 0)
        agents = 3
        lm = LoadManager(self.runtime_stats, agents, .5, 0)
        self.lm = lm
 
        cases, config = self.load_xml_cases()
        
        for req in cases:
            lm.add_req(req)
            
        
        lm.setDaemon(True)
        lm.start()
        
        self.console = Console(self.runtime_stats, self.agents_statlist, self.total_statlist)
        self.console.setDaemon(True)
        self.console.start()
        
        self.switch_status(True)
        
        
    def on_stop(self, evt):
        self.lm.stop()
        self.console.stop()
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
            if child.tag != dom.getroot().tag and child.tag == 'config':
                for element in child:
                    if element.tag == 'agents':
                        cfg = Config()                
                        cfg.agents = element.text
                    if element.tag == 'interval':
                        cfg.interval = element.text
                    if element.tag == 'rampup':
                        cfg.rampup = element.text
        return (cases, cfg)
   
        
    def switch_status(self, is_on):
        # change the status gauge and swap enablement of run/stop buttons
        if is_on:
            self.run_btn.Disable()
            self.stop_btn.Enable()
            self.busy_timer.Start(75)
        else:
            self.run_btn.Enable()
            self.stop_btn.Disable()
            self.busy_timer.Stop()




class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        


class Console(Thread):  # runs in its own thread so we don't block UI events      
    def __init__(self, runtime_stats, agents_statlist, total_statlist):
        Thread.__init__(self)
        self.runtime_stats = runtime_stats
        self.agents_statlist = agents_statlist
        self.total_statlist = total_statlist
        self.running = True
        self.refresh_rate = 2
        
    def run(self):
        start_time = time.time()
        while self.running:
            # refresh total monitor
            elapsed_secs = int(time.time() - start_time)  # running time in secs
            ids = self.runtime_stats.keys()
            agg_count = sum([self.runtime_stats[id].count for id in ids])  # total req count
            agg_total = sum([self.runtime_stats[id].total_latency for id in ids])
            agg_count = sum([self.runtime_stats[id].count for id in ids])
            agg_error_count = sum([self.runtime_stats[id].error_count for id in ids])
            if agg_count > 0:
                agg_avg = agg_total / agg_count  # total avg response time
            else: 
                agg_avg = 0
            self.total_statlist.DeleteAllItems()       
            index = self.total_statlist.InsertStringItem(sys.maxint, '%d' % elapsed_secs)
            self.total_statlist.SetStringItem(index, 1, '%d' % agg_count)
            self.total_statlist.SetStringItem(index, 2, '%d' % agg_error_count)
            self.total_statlist.SetStringItem(index, 3, '%.3f' % agg_avg)
            
            # refresh agents monitor
            self.agents_statlist.DeleteAllItems()       
            for id in self.runtime_stats.keys():
                index = self.agents_statlist.InsertStringItem(sys.maxint, '%d' % (id + 1))
                self.agents_statlist.SetStringItem(index, 1, '%d' % self.runtime_stats[id].count)
                self.agents_statlist.SetStringItem(index, 2, '%d' % self.runtime_stats[id].status)
                self.agents_statlist.SetStringItem(index, 3, '%.3f' % self.runtime_stats[id].latency)
                self.agents_statlist.SetStringItem(index, 4, '%.3f' % self.runtime_stats[id].avg_latency)
                
            time.sleep(self.refresh_rate)
    

    def stop(self):
        self.running = False
            
            
        



class Config():
    def __init__(self, agents=1, interval=1, rampup=0):
        self.agents = agents
        self.interval = interval
        self.rampup = rampup
            
            

def main():
    app = wx.App(0)
    Application(None)
    app.MainLoop()            

if __name__ == "__main__":
    main()
