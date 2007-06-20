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


import os
import time
import httplib2
from threading import Thread



class LoadManager(Thread):  # LoadManager runs in its own thread to decouple from its caller
    def __init__(self, runtime_stats, agents, interval, rampup):
        Thread.__init__(self)
        
        self.running = True
        
        self.agents = agents
        self.interval = interval
        self.rampup = rampup
        
        self.runtime_stats = self.init_runtime_stats(runtime_stats)
        
        self.agent_refs = []
        self.msg_queue = []
    
    
    def __create_output_dir(self):
        out_dir = 'output'
        if out_dir in os.listdir(os.getcwd()):
            for file in os.listdir(out_dir):
                os.remove(out_dir + '/' + file)
            os.rmdir(out_dir)
        os.mkdir(out_dir)
        
        
    def stop(self):
        self.running = False
        for agent in self.agent_refs:
            agent.stop()
        
        
    def run(self):
        self.running = True
        self.__create_output_dir()
        for i in range(self.agents):
            spacing = float(self.rampup) / float(self.agents)
            if i > 0:  # first agent starts right away
                time.sleep(spacing)
            if self.running:  # in case stop() was called
                self.error_queue = []
                
                agent = LoadAgent(i, self.interval, self.runtime_stats, self.error_queue, self.msg_queue)
                agent.start()
                self.agent_refs.append(agent)
                print 'started agent ' + str(i + 1)
    
    
    def init_runtime_stats(self, runtime_stats):
        for i in range(self.agents):
            runtime_stats[i] = StatCollection(0, '', 0, 0, 0, 0)
        return runtime_stats
    

    def add_req(self, req):
        self.msg_queue.append(req)
      
        


class LoadAgent(Thread):  # each agent runs in its own thread
    def __init__(self, id, interval, runtime_stats, error_queue, msg_queue):
        Thread.__init__(self)
        
        self.running = True
        self.resp_logging = False
        self.resp_log = None
        
        self.runtime_stats = runtime_stats  # shared stats dictionary
        self.id = id
        self.interval = interval
        self.msg_queue = msg_queue
        
        self.count = 0
        self.error_count = 0
        
        self.__enable_resp_logging()
        
        
    def stop(self):
        self.running = False
        self.__disable_resp_logging()
        
        
    def run(self):
        total_latency = 0
        while self.running:
            for req in self.msg_queue:
                # timed msg send
                start_time = time.time()
                resp, content = self.send(req)
                end_time = time.time()
                
                if resp.status >= 400:
                    self.error_count += 1
                self.count += 1
                
                content_bytes = len(content)
                
                latency = end_time - start_time
                total_latency += latency
                
                # update the shared stats dictionary
                self.runtime_stats[self.id] = StatCollection(resp.status, resp.reason, latency, self.count, self.error_count, total_latency)
                
                # log response
                log_date = time.strftime('%d %b %Y', time.localtime())
                log_time = time.strftime('%H:%M:%S', time.localtime())
                self.log_resp('%s,%s,%s,%s,%d,%s,%f' % (log_date, log_time, end_time, req.url, resp.status, resp.reason, latency))
 
                expire_time = (self.interval - latency)
                if expire_time > 0:
                    time.sleep(expire_time)  # sleep the rest of the interval so we keep even pacing
        
        
    def send(self, req):
        h = httplib2.Http()
        resp, content = h.request(req.url, req.method)
        return (resp, content)


    def log_resp(self, txt):
        if self.resp_logging:
            self.resp_log.write('%s\n' % txt)
            
            
    def __enable_resp_logging(self):
        self.resp_log = open('output/agent_%d_output.csv' % self.id, 'w')
        self.resp_logging = True
        
        
    def __disable_resp_logging(self):
        self.resp_log.close()
        self.resp_logging = False

            
            


class Request():
    def __init__(self, url='localhost', method='GET', body='', headers={}):
        self.url = url
        self.method = method
        self.body = body
        self.headers = headers
        
        if method == 'POST':
            self.headers['Content-type'] = 'text/xml'  # use application/x-www-form-urlencoded for Form POSTs
    
    
    def add_header(self, (key, value)):
        self.headers[key] = value
    
    
    def set_content_type(self, content_type):
        self.headers['Content-type'] = content_type
        



class StatCollection():
    def __init__(self, status, reason, latency, count, error_count, total_latency):
        self.status = status
        self.reason = reason
        self.latency = latency
        self.count = count
        self.error_count = error_count
        self.total_latency = total_latency
        if count > 0:
            self.avg_latency = total_latency / count
        else:
            self.avg_latency = 0

    