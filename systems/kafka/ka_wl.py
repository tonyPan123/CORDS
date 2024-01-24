#!/usr/bin/env  python

import sys
import os
import time
import subprocess
import logging
import random
import threading

def invoke_cmd(cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return (out, err)

#ZooKeeper-related Config
logging.basicConfig()
host_list = ['localhost', 'localhost', 'localhost']
port_list = [9791, 9792, 9793]

#ZooKeeper code home, log file names
#ZK_HOME = '~/legolas-target-systems/zookeeper/3.4.6/'
logfile_name1 = 'server.log'
logfile_name2 = 'state-change.log'


#Kill all Zookeeper Processes
os.system("pkill -f \'java.*zoo*\'")
os.system("pkill -f \'java.*zoo*\'")
os.system("pkill -f \'java.*kafka*\'")
os.system("pkill -f \'java.*kafka*\'")

server_dirs = []
log_dir = None

assert len(sys.argv) >= 4

# The CORDS framework passes the following arguments to the workload program
# zk_workload_read.py trace/cords workload_dir1 workload_dir2 .. workload_dirn log_dir

# For ZooKeeper we have three servers and hence three directories
for i in range(2, 5):
        server_dirs.append(sys.argv[i])

#if logdir specified
if len(sys.argv) >= 6:
        log_dir = sys.argv[-1]

# For now assume only 3 nodes

# Write the config files with the correct workload directories
config_files = []
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
for i in [0, 1, 2]:
        config_files.append((os.path.join(os.path.join(CURR_DIR, 'conf-'+str(i+1)+'.mp'), 'server.properties')))
        if ".mp" in server_dirs[i]: 
                os.system('cp ' + os.path.join(os.path.join(CURR_DIR, 'conf-'+str(i+1)+'.back'), 'server.properties')  + ' ' + config_files[i])
                print 'Mount' + config_files[i]
        else: 
                os.system('cp ' + os.path.join(os.path.join(CURR_DIR, 'conf-'+str(i+1)), 'server.properties')  + ' ' + config_files[i])



# Get rid of format stage 
#for i in range(0,3):
#	os.system('cp -R ' + os.path.join(CURR_DIR, 'store-'+str(i+1)+'.back') + ' ' + server_dirs[i])



# Start the ZooKeeper cluster
#for i in [0, 1, 2]:
        # chdir here so that zk can create the log here in this directory
#       os.chdir(server_dirs[i])
os.system(os.path.join(CURR_DIR, 'clean.sh '))
os.system(os.path.join(CURR_DIR, 'start-cluster.sh '))
#os.chdir(CURR_DIR)

time.sleep(10)

out = ''
err = ''
#present_value = '0000'

all_start = True
# Get state of ZooKeeper nodes before reading data
if log_dir is not None:
        client_log_file = os.path.join(log_dir, 'log-client')
        with open(client_log_file, 'w') as f:
                f.write('Before workload\n')
                out, err = invoke_cmd('ps aux | grep kafka')
                to_write = ''
                out = out.split('\n')
                out = [i for i in out if i is not None and len(i) > 0 and ('logs-1' in i or 'logs-2' in i or 'logs-3' in i)]
                to_check = ['logs-1', 'logs-2', 'logs-3']
                for check in to_check:
                        found = False
                        for i in out:
                                if check in i:
                                        found = True
                        to_write += check[:6] + ' running:' + str(found) + '\n'
                        if not found:
                                all_start = False

                f.write(to_write)
                f.write('----------------------------------------------\n')


cerr = []
cout = []

def create(server_index, file_index):  
        global rerr 
        global rout 
        returned = None
        out, err = invoke_cmd(os.path.join(CURR_DIR, 'client.sh') + ' ' + str(port_list[server_index]) + ' create  '+ str(server_index) + ' 5')
        cerr.append(err) 

workloads = []

for server_index in range(1, 4):
    buf = threading.Thread(target=lambda: read(server_index, file_index))
    buf.start()
    workloads.append(buf)

for workload in workloads :
        workload.join()

for s in cerr :
	print c
for s in cerr :
	print c

rerr = []
rout = []

# Issue Reads on all the nodes in the cluster and check its value
def consume(server_index, file_index, topic_index):  
        global rerr 
        global rout 
        returned = None
        topic = 'gray-' + str(file_index) + '-' + str(topic_index)
        out, err = invoke_cmd(os.path.join(CURR_DIR, 'client.sh') + ' ' + str(port_list[server_index]) + ' consume '+ topic + ' 0 100')
        rerr.append(err) 



werr = []
wout= []

# Write workload
def produce(server_index, file_index, topic_index):
        global werr 
        global wout   
        returned = None
        topic = 'gray-' + str(file_index) + '-' + str(topic_index)
        out, err = invoke_cmd(os.path.join(CURR_DIR, 'client.sh') + ' ' + str(port_list[server_index]) + ' produce '+ topic + ' 100')
        rerr.append(err) 



workloads = []
        
for server_index in range(1, 4):
    for file_index in range(1, 4):
        for topic_index in range(0, 5):
            buf = threading.Thread(target=lambda: read(server_index, file_index, topic_index))
            buf.start()
            workloads.append(buf)
            buf = threading.Thread(target=lambda: write(server_index, file_index, topic_index))
            buf.start()
            workloads.append(buf)

for workload in workloads :
        workload.join()

for s in rout :
	print s
for s in wout :
	print s
for s in rerr :
	print s
for s in werr :
	print s



# Get state of ZooKeeper nodes after reading data
if log_dir is not None:
        assert os.path.isdir(log_dir) and os.path.exists(log_dir)
        client_log_file = os.path.join(log_dir, 'log-client')
        with open(client_log_file, 'a') as f:
                f.write('out:\n' + str(out) + '\n')
                f.write('err:\n' + str(err) + '\n')
                for s in rout :
                        f.write(s + '\n')
                for s in wout :
                        f.write(s + '\n')
                for s in rerr :
                        f.write(s + '\n')
                for s in werr :
                        f.write(s + '\n')
                #f.write('rout:\n' + str(out) + '\n')
                #f.write('rerr:\n' + str(err) + '\n')
                #f.write('wout:\n' + str(out) + '\n')
                #f.write('werr:\n' + str(err) + '\n')
                #p = 0
                #f.write('CLUSTER STATE:\n')
                #for host in host_list:
                #        out, err = invoke_cmd('echo stat | nc ' + host + ' ' + str(port_list[p]) + ' | grep Mode')
                #        f.write(host + ':' + str(port_list[p]) + ':' + out.replace('\n', '') + '|'  + err.replace('\n', '') + '\n')
                #        p += 1

if log_dir is not None:
        client_log_file = os.path.join(log_dir, 'log-client')
        with open(client_log_file, 'a') as f:
                f.write('----------------------------------------------\n')
                f.write('After workload\n')
                out, err = invoke_cmd('ps aux | grep kafka')
                to_write = ''
                out = out.split('\n')
                out = [i for i in out if i is not None and len(i) > 0 and ('logs-1' in i or 'logs-2' in i or 'logs-3' in i)]
                to_check = ['logs-1', 'logs-2', 'logs-3']
                for check in to_check:
                        found = False
                        for i in out:
                                if check in i:
                                        found = True
                        to_write += check[:6] + ' running:' + str(found) + '\n'

                f.write(to_write)

time.sleep(3)
# Kill the ZooKeeper nodes
os.system("pkill -f \'java.*kafka*\'")
os.system("pkill -f \'java.*zoo*\'")
time.sleep(1)


#os.system("sudo chown -R $USER:$USER store*")

#for i in [0, 1, 2]:
#       os.system('rm -rf ' + config_files[i])

# if log_dir specified
if log_dir is not None:
        for i in range(0, len(server_dirs)):
                os.system('cp ' + os.path.join(os.path.join(CURR_DIR, 'output-'+str(i+1)), logfile_name1)  + ' ' + os.path.join(log_dir, 'log-'+str(i)))
                os.system('cp ' + os.path.join(os.path.join(CURR_DIR, 'output-'+str(i+1)), logfile_name2)  + ' ' + os.path.join(log_dir, 'state-'+str(i)))