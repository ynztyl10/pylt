#
#    Copyright (c) 2007-2008 Corey Goldberg (corey@goldb.org)
#    License: GNU GPLv3
#
#    This file is part of Pylot.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License 
#    for more details.
#


import os
import re
import time
import pickle
import lib.httplib2 as httplib2
import results
from threading import Thread



class LoadManager(Thread):
    def __init__(self, num_agents, interval, rampup, log_resps, runtime_stats, error_queue):
        Thread.__init__(self)
        
        self.running = True
        self.num_agents = num_agents
        self.interval = interval
        self.rampup = rampup
        self.log_resps = log_resps
        
        self.output_dir = time.strftime('results/results_%Y.%m.%d_%H.%M.%S', time.localtime()) 
        
        self.runtime_stats = self.init_runtime_stats(runtime_stats)
        self.workload = {'num_agents': num_agents, 'interval': interval * 1000, 'rampup': rampup}  # convert interval from secs to millisecs
        self.error_queue = error_queue
        
        self.agent_refs = []
        self.msg_queue = []
            
        
    def stop(self):
        self.running = False
        for agent in self.agent_refs:
            agent.stop()
        self.store_for_post_processing(self.output_dir, self.runtime_stats, self.workload)  # pickle dictionaries to files for results post-processing
        
        # auto-generate results when test is stopped
        self.results_gen = results.ResultsGenerator(self.output_dir)
        self.results_gen.setDaemon(True)
        self.results_gen.start()
        
    
    def run(self):
        self.running = True
        self.agents_started = False
        try:
            os.mkdir(self.output_dir)
        except:
            os.mkdir('results')
            os.mkdir(self.output_dir)
        for i in range(self.num_agents):
            spacing = float(self.rampup) / float(self.num_agents)
            if i > 0:  # first agent starts right away
                time.sleep(spacing)
            if self.running:  # in case stop() was called before all agents are started
                agent = LoadAgent(i, self.interval, self.log_resps, self.output_dir, self.runtime_stats, self.error_queue, self.msg_queue)
                agent.start()
                self.agent_refs.append(agent)
                print 'Started agent ' + str(i + 1)
        print 'All agents running...\n\n'
        self.agents_started = True
        
    
    def init_runtime_stats(self, runtime_stats):
        for i in range(self.num_agents):
            runtime_stats[i] = StatCollection(0, '', 0, 0, 0, 0, 0)
        return runtime_stats
    

    def add_req(self, req):
        self.msg_queue.append(req)
        
    
    def store_for_post_processing(self, dir, runtime_stats, workload):
        fh = open(dir + '/agent_detail.dat', 'w')
        pickle.dump(runtime_stats, fh)
        fh.close()
        fh = open(dir + '/workload_detail.dat', 'w')
        pickle.dump(workload, fh)
        fh.close()         




class LoadAgent(Thread):  # each agent runs in its own thread
    def __init__(self, id, interval, log_resps, output_dir, runtime_stats, error_queue, msg_queue):
        Thread.__init__(self)
        
        self.running = True
        self.id = id
        self.interval = interval
        self.log_resps = log_resps
        self.output_dir = output_dir
        
        # log options
        self.stat_logging = True
        self.trace_logging = False
        if self.log_resps:
            self.enable_trace_logging()
            
        self.runtime_stats = runtime_stats  # shared stats dictionary
        self.error_queue = error_queue  # shared error list
        self.msg_queue = msg_queue # shared message/request queue
        
        self.count = 0
        self.error_count = 0
        
        
        
        
        # create the http object here and reuse it for every fetch
        # httplib2 seems to be a bit buggy, so this is a workaround for a problem
        # it's causing in longer running tests with lots of agents (90+)
        self.http = httplib2.Http()
        

    def stop(self):
        self.running = False
        if self.trace_logging:
            self.disable_trace_logging()
        
        
    def run(self):
        total_latency = 0
        total_bytes = 0
        while self.running:
            for req in self.msg_queue:
                for repeat in range(req.repeat):
                    if self.running:
                        sock_err = False
                        
                        # timed msg send
                        start_time = time.time()
                        try:
                            resp, content = self.send(req)
                        except:
                            # a connection error may occur 
                            # It's good to log that one too, otherwise exceptions fro httplib2 will start to pop up
                            resp = SockErr()
                            content = ''
                        end_time = time.time()  # epoch
                        
                        # get times for logging and error display
                        tmp_time = time.localtime()
                        cur_date = time.strftime('%d %b %Y', tmp_time)
                        cur_time = time.strftime('%H:%M:%S', tmp_time)
                        
                        # check verifications and status code for errors
                        is_error = False
                        if resp.status >= 400 or resp.status == 0:
                            is_error = True
                        if not req.verify == '':
                            if not re.search(req.verify, content, re.DOTALL): 
                                is_error = True
                        if not req.verify_negative == '':
                            if re.search(req.verify_negative, content, re.DOTALL):
                                is_error = True
                    
                        if is_error:                    
                            self.error_count += 1
                            # put an error message on the queue
                            error_string = 'Agent %s:  %s - %d %s,  url: %s' % (self.id + 1, cur_time, resp.status, resp.reason, req.url)
                            self.error_queue.append(error_string)
                            # log the error
                            self.log_error(error_string)
                            
                        self.count += 1
                            
                        resp_bytes = len(content)
                        total_bytes += resp_bytes
                        latency = end_time - start_time
                        total_latency += latency
                        
                        # update shared stats dictionary
                        self.runtime_stats[self.id] = StatCollection(resp.status, resp.reason, latency, self.count, self.error_count, total_latency, total_bytes)
                        
                        # log response stats/info
                        if self.stat_logging:
                            self.log_stat('%s|%s|%s|%s|%d|%s|%d|%f' % (cur_date, cur_time, end_time, req.url, resp.status, resp.reason, resp_bytes, latency))
                        
                        # log response content
                        if self.trace_logging:
                            for key in resp:
                                self.log_trace('%s: %s' % (key, resp[key]))
                            self.log_trace('\n\n%s' % content)
                            self.log_trace('\n\n************************* LOG SEPARATOR *************************\n\n')
                            
                        expire_time = (self.interval - latency)
                        if expire_time > 0:
                            time.sleep(expire_time)  # sleep the remainder of the interval so we keep even pacing
                    
                    else:  # don't go through the entire range if stop has been called
                        break
        
        
    def send(self, req):
        headers = {}
        body = ''
        if req.headers:
            headers = req.headers
        if req.body:
            body = req.body
        resp, content = self.http.request(req.url, method=req.method, body=body, headers=headers)
        return (resp, content)

    
    def log_stat(self, txt):\
        # catch exception if IOError occurs
        # some systems have a limit of the number of files
        # that can be open at the same time
        try:
            stat_log = open('%s/agent_%d_stats.psv' % (self.output_dir, self.id + 1), 'a')
            stat_log.write('%s\n' % txt)
            stat_log.flush()  # flush write buffer so we always log in real-time
            stat_log.close()
        except: 
            print 'Error writing to stats file\n'
    
    
    def log_error(self, txt):
        # catch exception if IOError occurs
        # some systems have a limit of the number of files
        # that can be open at the same time
        try:
            error_log = open('%s/agent_%d_errors.log' % (self.output_dir, self.id + 1), 'a')
            error_log.write('%s\n' % txt)
            error_log.flush()
            error_log.close()
        except: 
        print 'Error writing to log file\n'
    
    
    def log_trace(self, txt):
        self.trace_log.write('%s\n' % txt)
        self.trace_log.flush()
            
            
    def enable_trace_logging(self):
        self.trace_log = open('%s/agent_%d.log' % (self.output_dir, self.id + 1), 'w')
        self.trace_logging = True
        
        
    def disable_trace_logging(self):
        self.trace_log.close()
        self.trace_logging = False
        
            


class Request():
    def __init__(self, url='localhost', method='GET', body='', headers={}, repeat=1):
        self.url = url
        self.method = method
        self.body = body
        self.headers = headers
        self.repeat = repeat
        
        # verification string or regex
        self.verify = ''
        self.verify_negative = ''
            
    
    def add_header(self, header_name, value):
        self.headers[header_name] = value
        



class SockErr(dict):
    def __init__(self):
        self['status'] = 0
        self['reason'] = 'Connection error'
        self.status = 0
        self.reason = 'Connection error'




class StatCollection():
    def __init__(self, status, reason, latency, count, error_count, total_latency, total_bytes):
        self.status = status
        self.reason = reason
        self.latency = latency
        self.count = count
        self.error_count = error_count
        self.total_latency = total_latency
        self.total_bytes = total_bytes
        if count > 0:
            self.avg_latency = total_latency / count
        else:
            self.avg_latency = 0

    