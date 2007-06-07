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
        
        self.running = True
        
        self.agents = agents
        self.interval = interval
        self.rampup = rampup
        self.runtime_stats = self.init_runtime_stats(runtime_stats)
        
        self.agent_refs = []
        self.msg_queue = []
        
        
    def stop(self):
        self.running = False
        for agent in self.agent_refs:
            agent.stop()
        
        
    def run(self):
        self.running = True
        for i in range(self.agents):
            spacing = (i * (float(self.rampup) / float(self.agents)))
            time.sleep(spacing)
            
            if self.running:  # check here in case stop() was called
                agent = LoadAgent(self.runtime_stats, i, self.interval, self.msg_queue)
                agent.start()
                self.agent_refs.append(agent)
                print 'started agent ' + str(i + 1)


    def init_runtime_stats(self, runtime_stats):
        for i in range(self.agents):
            runtime_stats[i] = StatCollection(0, '', 0, 0)
        return runtime_stats


    def add_req(self, req):
        self.msg_queue.append(req)
      
        


class LoadAgent(Thread):  # each agent runs in its own thread
    def __init__(self, runtime_stats, id, interval, msg_queue):
        Thread.__init__(self)
        
        self.running = True
        self.resp_logging = False
        self.resp_log = None
        
        self.runtime_stats = runtime_stats
        self.id = id
        self.interval = interval
        self.msg_queue = msg_queue
        
        self.count = 0
        
        self.__enable_resp_logging()
        
        
    def stop(self):
        self.running = False
        self.__disable_resp_logging()
        
        
    def run(self):
        while self.running:
            for req in self.msg_queue:
                start_time = time.time()
                try:
                    resp = self.send(req)
                except:
                    resp = None
                self.count += 1
                end_time = time.time()
                latency = end_time - start_time
                if resp:
                    # update the shared stats dictionary
                    self.runtime_stats[self.id] = StatCollection(resp.status, resp.reason, latency, self.count)
                    # log response
                    log_date = time.strftime('%d %b %Y', time.localtime())
                    log_time = time.strftime('%H:%M:%S', time.localtime())
                    self.log_resp('%s,%s,%s,%d,%s,%f' % (log_date, log_time, end_time, resp.status, resp.reason, latency))
                expire_time = (self.interval - latency)
                if expire_time > 0:
                    time.sleep(expire_time)
        
        
    def send(self, req):
        conn = httplib.HTTPConnection(req.host)
        #conn.set_debuglevel(1)
        try:
            conn.request(req.method, req.path, req.body, req.headers)
            resp = conn.getresponse()
            return resp
        except:
            raise  # rethrow exception


    def log_resp(self, txt):
        if self.resp_logging:
            self.resp_log.write('%s\n' % txt)
            
            
    def __enable_resp_logging(self):
        self.resp_log = open('agent_%d_output.csv' % self.id, 'w')
        self.resp_logging = True
        
        
    def __disable_resp_logging(self):
        self.resp_log.close()
        self.resp_logging = False

            
            
            


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

    