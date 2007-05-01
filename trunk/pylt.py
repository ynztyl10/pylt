#!/usr/bin/env python

#    Copyright (c) 2007, Corey Goldberg (corey@goldb.org)
#
#    This file is part of PyLT.
#
#    PyLT is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.


import time
import os
import httplib
from threading import Thread


class LoadManager:
    def __init__(self):
        self.thread_refs = []
        self.msg = ('localhost', 'GET', '/')
    
    def stop(self):
        for thread in self.thread_refs:
            thread.stop()
            
    def start(self, threads=1, interval=0, rampup=1):
        for i in range(threads):
            spacing = (i * (float(rampup) / float(threads)))
            time.sleep(spacing)
            agent = LoadAgent(interval, self.msg)
            agent.start()
            print 'started thread # ' + str(i + 1)
            self.thread_refs.append(agent)
        

class LoadAgent(Thread):
    def __init__(self, interval, msg):
        Thread.__init__(self)
        self.running = True
        self.interval = interval
        self.msg = msg
        
    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            start_time = time.time()
            self.send(self.msg)
            end_time = time.time()
            raw_latency = end_time - start_time
            latency = ('%.3f' % raw_latency)
            
            print latency
            
            expire_time = (self.interval - raw_latency)
            if expire_time > 0:
                time.sleep(expire_time)
                
    def send(self, msg):
        conn = httplib.HTTPConnection(msg[0])
        try:
            conn.request(msg[1], msg[2])
            body = conn.getresponse().read()
        except:
            print "failed request"




# sample script:
def main():
    lm = LoadManager()
    lm.msg = ('www.example.com', 'GET', '/')
    lm.start(threads=4, interval=10, rampup=5)
    
if __name__ == "__main__":
    main()