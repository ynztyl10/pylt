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
        self.root.title('PyLT - HTTP Load Test')
        self.root.configure(background='#EFEFEF')
       
        canvas = Canvas(self.root, width=215, height=60, background='#EFEFEF', highlightthickness=0)
        canvas.place(x=0, y=0)

        Label(self.root, text='TS Interval', background='#EFEFEF').place(x=15, y=115)
        interval_entry = Entry(self.root, width=3)
        interval_entry.place(x=78, y=115)
        interval_entry.insert(0, '0')
        self.interval_entry = interval_entry
        
        
        
        Button(self.root, text='Run', command=self.run, width=15).place(x=15, y=165)
        
        
        Label(self.root, text='Run Num', background='#EFEFEF').place(x=15, y=140)
        prefix_entry = Entry(self.root, width=6)
        prefix_entry.place(x=78, y=140)
        prefix_entry.insert(0, '')
        self.prefix_entry = prefix_entry
                
        text_box = Text(self.root, background='#CCCCCC', width=75, height=16)
        text_box.place(x=130, y=70)
        self.text_box = text_box
    
    

        
        

    
    def run(self):
        lm = LoadManager(self.runtime_stats, 3, .5, 3)
        #lm = LoadManager(self.runtime_stats, agents, interval, rampup)
        lm.add_req(Request('www.goldb.org'))
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
        
    def run(self):
        time.sleep(2) # pause before first stat refresh
        while True:
            self.text_box.delete(1.0, END)
            for id in self.runtime_stats.keys():
                self.text_box.insert(INSERT, id)
                self.text_box.insert(INSERT, ' - ')       
                self.text_box.insert(INSERT, self.runtime_stats[id].count)
                self.text_box.insert(INSERT, ' - ')
                self.text_box.insert(INSERT, self.runtime_stats[id].status)
                self.text_box.insert(INSERT, ' ')
                self.text_box.insert(INSERT, self.runtime_stats[id].reason)
                self.text_box.insert(INSERT, ' - ')
                self.text_box.insert(INSERT, '%.3f' % self.runtime_stats[id].latency)                
                self.text_box.insert(INSERT, '\n')
            
            print '------'
            
            for id in self.runtime_stats.keys():
                print '%d - %d - %d %s - %.3f' %  (
                    id,
                    self.runtime_stats[id].count,                
                    self.runtime_stats[id].status,
                    self.runtime_stats[id].reason,
                    self.runtime_stats[id].latency
                )
                
            time.sleep(self.refresh_rate)




def main():
    root = Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()
