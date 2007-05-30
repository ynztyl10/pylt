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
import os
import httplib
from threading import Thread



class LoadManager(Thread):  # LoadManager runs in its own thread to decouple from the Controller
    def __init__(self, runtime_stats, agents, interval, rampup):
        Thread.__init__(self)
        
        self.agents = agents
        self.interval = interval
        self.rampup = rampup
        
        self.thread_refs = []
        self.msg_queue = []
        self.runtime_stats = runtime_stats
        
    def stop(self):
        for thread in self.thread_refs:
            thread.stop()
            
    def run(self):
        for i in range(self.agents):
            spacing = (i * (float(self.rampup) / float(self.agents)))
            time.sleep(spacing)
            
            agent = LoadAgent(self.runtime_stats, i, self.interval, self.msg_queue)
            agent.start()
            
            print 'started agent ' + str(i)
            self.thread_refs.append(agent)

    def add_req(self, req):
        self.msg_queue.append(req)
      
        
        


class LoadAgent(Thread):  # each agent runs in its own thread
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
    c = Controller()
    c.start(agents=3, interval=2, rampup=0)
    c.add_req(Request('www.goldb.org'))
    c.run()
    
if __name__ == "__main__":
    main()
    