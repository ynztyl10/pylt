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
import sys
import time
import pickle
import Queue
import lib.httplib2 as httplib2
import results
from threading import Thread




class LoadManager(Thread):
    def __init__(self, num_agents, interval, rampup, log_resps, runtime_stats, error_queue, output=None, test_name=None):
        Thread.__init__(self)
        
        self.running = True
        self.num_agents = num_agents
        self.interval = interval
        self.rampup = rampup
        self.log_resps = log_resps
        self.runtime_stats = runtime_stats
        self.test_name = test_name
        
        if output:
            self.output_dir = output
        else:
            if test_name:
                self.output_dir = time.strftime('results/' + test_name + '_' + 'results_%Y.%m.%d_%H.%M.%S', time.localtime())
            else:
                self.output_dir = time.strftime('results/results_%Y.%m.%d_%H.%M.%S', time.localtime()) 
        
        # initialize the stats
        for i in range(self.num_agents): 
            self.runtime_stats[i] = StatCollection(0, '', 0, 0, 0, 0, 0)
            
        self.workload = {'num_agents': num_agents, 'interval': interval * 1000, 'rampup': rampup}  # convert interval from secs to millisecs
        self.error_queue = error_queue
        
        self.results_queue = Queue.Queue()  # result stats get queued up by agent threads
        self.agent_refs = []
        self.msg_queue = []  # list of Request objects
        
    
    def run(self):
        self.running = True
        self.agents_started = False
        try:
            os.makedirs(self.output_dir, 0755)
        except OSError:
            self.output_dir = self.output_dir + time.strftime('/results_%Y.%m.%d_%H.%M.%S', time.localtime())
            try:
               os.makedirs(self.output_dir, 0755)
            except OSError:
                print 'ERROR: Can not create output directory'
                sys.exit(1)
        
        # start thread for reading and writing queued results
        self.results_writer = ResultWriter(self.results_queue, self.output_dir)
        self.results_writer.setDaemon(True)
        self.results_writer.start()
        
        for i in range(self.num_agents):
            spacing = float(self.rampup) / float(self.num_agents)
            if i > 0:  # first agent starts right away
                time.sleep(spacing)
            if self.running:  # in case stop() was called before all agents are started
                agent = LoadAgent(i, self.interval, self.log_resps, self.output_dir, self.runtime_stats, self.error_queue, self.msg_queue, self.results_queue)
                agent.start()
                self.agent_refs.append(agent)
                agent_started_line = 'Started agent ' + str(i + 1) 
                if sys.platform.startswith('win'):
                    sys.stdout.write(chr(0x08) * len(agent_started_line))
                    sys.stdout.write(agent_started_line)
                else:
                    esc = chr(27) # escape key
                    sys.stdout.write(esc + '[G' )
                    sys.stdout.write(esc + '[A' )
                    sys.stdout.write(agent_started_line + '\n')
        if sys.platform.startswith('win'):
            sys.stdout.write('\n')
        print '\nAll agents running...\n\n'
        self.agents_started = True
        
    
    def stop(self):
        self.running = False
        for agent in self.agent_refs:
            agent.stop()
        self.store_for_post_processing(self.output_dir, self.runtime_stats, self.workload)  # pickle dictionaries to files for results post-processing
        
        self.results_writer.stop()
        
        # auto-generate results from a new thread when the test is stopped
        self.results_gen = results.ResultsGenerator(self.output_dir, self.test_name)
        self.results_gen.setDaemon(True)
        self.results_gen.start()


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
    def __init__(self, id, interval, log_resps, output_dir, runtime_stats, error_queue, msg_queue, results_queue):
        Thread.__init__(self)
        
        self.running = True
        self.id = id
        self.interval = interval
        self.log_resps = log_resps
        self.output_dir = output_dir
            
        self.runtime_stats = runtime_stats  # shared stats dictionary
        self.error_queue = error_queue  # shared error list
        self.msg_queue = msg_queue  # shared message/request queue
        self.results_queue = results_queue  # shared results queue
        
        self.count = 0
        self.error_count = 0
        
        # choose timer to use:
        if sys.platform.startswith('win'):
            self.default_timer = time.clock  # time.clock() is more precise on Windows systems
        else:
            self.default_timer = time.time  # time.time() is more precise on Linux/Unix and most other platforms 
            
        self.trace_logging = False
        if self.log_resps:
            self.enable_trace_logging()
            
        # create the http object here and reuse it for every fetch.
        # httplib2 seems to be a bit buggy, so this is a workaround for a problem
        # it's causing in longer running tests with lots of agents (90+)
        self.http = httplib2.Http()
        
        
    def run(self):
        total_latency = 0
        total_bytes = 0
        while self.running:
            for req in self.msg_queue:
                for repeat in range(req.repeat):
                    if self.running:

                        # timed msg send
                        start_time = self.default_timer()
                        try:
                            resp, content = self.send(req)
                        except:
                            # connection error may occur and exceptions from httplib2 will be thrown
                            resp = SockErr()
                            content = ''
                        end_time = self.default_timer()
                        
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
                            error_string = 'Agent %s:  %s - %d %s,  url: %s' % (self.id + 1, cur_time, resp.status, resp.reason, req.url)
                            self.error_queue.append(error_string)
                            self.log_error(error_string)
                            
                        self.count += 1
                            
                        resp_bytes = len(content)
                        total_bytes += resp_bytes
                        latency = end_time - start_time
                        total_latency += latency
                        
                        # update shared stats dictionary
                        self.runtime_stats[self.id] = StatCollection(resp.status, resp.reason, latency, self.count, self.error_count, total_latency, total_bytes)
                        
                        # put response stats/info on queue for reading by the consumer (ResultWriter) thread
                        q_tuple = (self.id + 1, cur_date, cur_time, end_time, req.url, resp.status, resp.reason, resp_bytes, latency)
                        self.results_queue.put(q_tuple)

                        # log response content
                        if self.trace_logging:
                            for key in resp:
                                self.log_trace('%s: %s' % (key, resp[key]))
                            self.log_trace('\n\n%s' % content)
                            self.log_trace('\n\n************************* LOG SEPARATOR *************************\n\n')
                            
                        expire_time = (self.interval - latency)
                        if expire_time > 0:
                            time.sleep(expire_time)  # sleep remainder of interval so we keep even pacing
                    
                    else:  # don't go through entire range if stop has been called
                        break
        
        
    def stop(self):
        self.running = False
        if self.trace_logging:
            self.disable_trace_logging()
            
            
    def send(self, req):
        headers = {}
        body = ''
        if req.headers:
            headers = req.headers
        if req.body:
            body = req.body
        resp, content = self.http.request(req.url, method=req.method, body=body, headers=headers)
        return (resp, content)

    
    
    def log_error(self, txt):
        try:
            error_log = open('%s/agent_%d_errors.log' % (self.output_dir, self.id + 1), 'a')
            error_log.write('%s\n' % txt)
            error_log.flush()
            error_log.close()
        except IOError, e: 
            print 'ERROR: can not write to error log file\n'
    
    
    def log_trace(self, txt):
        self.trace_log.write('%s\n' % txt)
        self.trace_log.flush()
            
            
    def enable_trace_logging(self):
        self.trace_log = open('%s/agent_%d.log' % (self.output_dir, self.id + 1), 'w')
        self.trace_logging = True
        
        
    def disable_trace_logging(self):
        self.trace_log.flush()
        self.trace_log.close()
        self.trace_logging = False
        
            


class Request():
    def __init__(self, url='localhost', method='GET', body='', headers=None, repeat=1):
        self.url = url
        self.method = method
        self.body = body
        self.repeat = repeat
        
        if headers:
            self.headers = headers
        else:
            self.headers = {}

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

    


class ResultWriter(Thread):
    #  this thread is for reading queued results and writing them to a log file.
    def __init__(self, results_queue, output_dir):
        Thread.__init__(self)
        self.running = True
        self.results_queue = results_queue
        self.output_dir = output_dir        

    def run(self):
        # TODO: Fix this:
        #  somewhere in here is what is causing the interpreter crash on Ctrl-C keyboard interrupt
        #  this is a bug in the Python interpreter
        #  see:  http://bugs.python.org/issue5160
        #  the workaround is to create the worker queues in the main thread.
        #
        f = open('%s/agent_stats.psv' % self.output_dir, 'a') 
        while self.running:
            try:
                q_tuple = self.results_queue.get(False)
                f.write('%s|%s|%s|%s|%s|%d|%s|%d|%f\n' % q_tuple)
                f.flush()
            except Queue.Empty:
                # re-check queue for messages every x sec
                time.sleep(.1)
                
    def stop(self):
        self.running = False


