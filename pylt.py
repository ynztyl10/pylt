#!/usr/bin/env python

#    Copyright (c) 2007 Corey Goldberg (corey@goldb.org)
#    License: GNU GPLv2
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





class Controller():
    pass




class LoadManager():
    def __init__(self):
        self.refresh_rate = 5
        self.thread_refs = []
        self.msg_queue = []
        self.runtime_stats = {}
        
    def stop(self):
        for thread in self.thread_refs:
            thread.stop()
            
    def start(self, threads=1, interval=0, rampup=1):
        for i in range(threads):
            spacing = (i * (float(rampup) / float(threads)))
            time.sleep(spacing)
            
            agent = LoadAgent(self.runtime_stats, i, interval, self.msg_queue)
            agent.start()
            
            print 'started thread ' + str(i)
            self.thread_refs.append(agent)
            
            
        time.sleep(2) # pause before first stat refresh
        while True:
            print '----'
            for id in self.runtime_stats.keys():
                print '%d - %d - %d %s - %.3f' %  (
                    id,
                    self.runtime_stats[id].count,                
                    self.runtime_stats[id].status,
                    self.runtime_stats[id].reason,
                    self.runtime_stats[id].latency
                )
            time.sleep(self.refresh_rate)

    def add_req(self, req):
        self.msg_queue.append(req)
      
        
        


class LoadAgent(Thread):
    def __init__(self, runtime_stats, id, interval, msg_queue):
        Thread.__init__(self)
        self.id = id
        self.running = True
        self.interval = interval
        self.msg_queue = msg_queue
        self.runtime_stats = runtime_stats
        self.count = 1
        
    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            for req in self.msg_queue:
                start_time = time.time()
                resp = self.send(req)
                end_time = time.time()
                
                latency = end_time - start_time
                response = resp.read()
                
                self.runtime_stats[self.id] = StatCollection(resp.status, resp.reason, latency, self.count)
        
                expire_time = (self.interval - latency)
                if expire_time > 0:
                    time.sleep(expire_time)
                
                self.count += 1
                
    def send(self, req):
        conn = httplib.HTTPConnection(req.host)
        #conn.set_debuglevel(1)
        try:
            conn.request(req.method, req.path, req.body, req.headers)
            resp = conn.getresponse()
            return resp
        except:
            print "failed request"






class Request():
    def __init__(self, host, method='GET', path='/', body='', headers={}):
        self.host = host
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers
        
        if method == 'POST':
            self.headers['Content-type'] = 'text/xml'  # use application/x-www-form-urlencoded for Form POSTs
    
    def add_header(self, (key, value)):
        self.headers[key] = value
    
    def set_content_type(self, content_type):
        self.headers['Content-type'] = content_type
        



class StatCollection():
    def __init__(self, status, reason, latency, count):
        self.status = status
        self.reason = reason
        self.latency = latency
        self.count = count
        
        
        

# sample script:
def main():
    lm = LoadManager()
    lm.add_req(Request('www.goldb.org'))
    #%lm.think_time(3.0)
    lm.start(threads=3, interval=2, rampup=0)
    
if __name__ == "__main__":
    main()
    