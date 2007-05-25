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





class LoadManager():
    def __init__(self):
        self.thread_refs = []
        self.msg_queue = []
        
    def stop(self):
        for thread in self.thread_refs:
            thread.stop()
            
    def start(self, threads=1, interval=0, rampup=1):
        for i in range(threads):
            spacing = (i * (float(rampup) / float(threads)))
            time.sleep(spacing)
            agent = LoadAgent(i, interval, self.msg_queue)
            agent.start()
            print 'started thread ' + str(i)
            self.thread_refs.append(agent)
    
    def add_msg(self, msg):
        self.msg_queue.append(msg)
      
        
        

class LoadAgent(Thread):
    def __init__(self, id, interval, msg_queue):
        Thread.__init__(self)
        self.id = id
        self.running = True
        self.interval = interval
        self.msg_queue = msg_queue
        
    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            for msg in self.msg_queue:
                start_time = time.time()
                resp = self.send(msg)
                end_time = time.time()
                
                raw_latency = end_time - start_time
                latency = ('%.3f' % raw_latency)
                
                body = resp.read()
                headers = resp.read()
                status = resp.status
                reason = resp.reason
                
                print ('%s - %s' % (self.id, latency))
                print status, reason
        
                expire_time = (self.interval - raw_latency)
                if expire_time > 0:
                    time.sleep(expire_time)
                
    def send(self, msg):
        conn = httplib.HTTPConnection(msg.host)
        #conn.set_debuglevel(1)
        try:
            conn.request(msg.method, msg.path, msg.body, msg.headers)
            resp = conn.getresponse()
            return resp
        except:
            print "failed request"






class Message():
    def __init__(self, host, method='GET', path='/', body='', headers={}):
        self.host = host
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers
        
        if method == 'POST':
            self.headers['Content-type'] = 'text/xml'  # default to text/xml
    
    def add_header(self, (key, value)):
        self.headers[key] = value
    
    def set_content_type(self, content_type):
        self.headers['Content-type'] = content_type
        


# sample script:
def main():
    lm = LoadManager()
    lm.add_msg(Message('www.goldb.org'))
    lm.start(threads=1, interval=2, rampup=0)
    
if __name__ == "__main__":
    main()
    