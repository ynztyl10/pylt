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
from pylt_engine import *

 

class Application:
    def __init__(self, root):
        self.root = root
        self.refresh_rate = 5
        self.runtime_stats = {}
        
        self.initialization()


    def initialization(self):
        self.root.geometry('%dx%d%+d%+d' % (600, 300, 200, 100))
        mono_font = ('Courier', 8)
        self.root.title('PyLT - HTTP Load Test')
        self.root.configure(background='#EFEFEF')
       
        canvas = Canvas(self.root, width=215, height=60, background='#EFEFEF', highlightthickness=0)
        canvas.place(x=0, y=0)




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
        
        col_labels = 'Agent #  | Count    | Response | Latency'
        
        
        Label(self.root, text=col_labels, background='#EFEFEF', font=mono_font).place(x=130, y=49)
        
        Button(self.root, text='Start', command=self.run, width=15).place(x=15, y=165)
        
        
        #Label(self.root, text='Run Num', background='#EFEFEF').place(x=15, y=140)
        #prefix_entry = Entry(self.root, width=6)
        #prefix_entry.place(x=78, y=140)
        #prefix_entry.insert(0, '')
        #self.prefix_entry = prefix_entry
        
        

        text_box = Text(self.root, background='#CCCCCC', font=mono_font, width=75, height=16)
        text_box.place(x=130, y=70)
        self.text_box = text_box
    
    

        
        

    
    def run(self):
        lm = LoadManager(self.runtime_stats, 3, .5, 3)
        #lm = LoadManager(self.runtime_stats, agents, interval, rampup)
        
        reqs = [
            Request('www.goldb.org'),
        ]
        
        for req in reqs:
            lm.add_req(req)
        
        
        lm.setDaemon(True)
        lm.start()
        
        c = Console(self.runtime_stats, self.refresh_rate, self.text_box)
        c.setDaemon(True)
        c.start()

        


  
class Console(Thread): # Monitoring Console runs in its own thread so we don't block UI events      
    def __init__(self, runtime_stats, refresh_rate, text_box):
        Thread.__init__(self)
        self.runtime_stats = runtime_stats
        self.refresh_rate = refresh_rate
        self.text_box = text_box
        self.logging = False
        
    def run(self):
        self.text_box.insert(INSERT, 'starting agents... ') 
        time.sleep(2) # pause before first stat refresh
        while True:
            self.text_box.delete(1.0, END)
            for id in self.runtime_stats.keys():
                gui_col_width = 8
                col_separator = ' | '
                self.text_box.insert(INSERT, self.pad_txt(gui_col_width, str(id + 1)))
                self.text_box.insert(INSERT, col_separator)       
                self.text_box.insert(INSERT, self.pad_txt(gui_col_width, str(self.runtime_stats[id].count)))
                self.text_box.insert(INSERT, col_separator)
                self.text_box.insert(INSERT, self.pad_txt(gui_col_width, str(self.runtime_stats[id].status)))
                self.text_box.insert(INSERT, col_separator)
                self.text_box.insert(INSERT, self.pad_txt(gui_col_width, '%.3f' % self.runtime_stats[id].latency))                
                self.text_box.insert(INSERT, '\n')
            
            if self.logging:
                print '----------'
                for id in self.runtime_stats.keys():
                    print '%d|%d|%d|%.3f' %  (
                        id + 1,
                        self.runtime_stats[id].count,                
                        self.runtime_stats[id].status,
                        self.runtime_stats[id].latency
                    )
                
            time.sleep(self.refresh_rate)

    def pad_txt(self, length, txt):
        pad_length = length - len(txt)
        padded_txt = txt
        padding = ''
        for l in range(pad_length):
            padding += ' ' 
        return txt + padding 
    

def main():
    root = Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()
