#!/usr/bin/env  python

import sys
import os
import time
import subprocess
import logging
from kazoo.client import KazooClient
from kazoo.client import KazooRetry
import random
import threading

def invoke_cmd(cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return (out, err)

#ZooKeeper-related Config
logging.basicConfig()
host_list = ['localhost', 'localhost', 'localhost']
port_list = [10712, 10713, 10714]
admin_list = [8080, 8081, 8082]
config_info = '''tickTime=2000\ndataDir=%s\nclientPort=%s\ninitLimit=10\nsyncLimit=5\nsnapCount=100\nadmin.serverPort=%s\nserver.1=localhost:10814:10916\nserver.2=localhost:10815:10917\nserver.3=localhost:10816:10918'''

#ZooKeeper code home, log file names
#ZK_HOME = '~/legolas-target-systems/zookeeper/3.4.6/'
ZK_HOME = '~/zookeeper/'
zoo_logfile_name = 'zookeeper-tonypan-server-razor15.out'

#Kill all Zookeeper Processes
os.system("pkill -f \'java.*zoo*\'")
os.system("pkill -f \'java.*zoo*\'")

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
server_configs = []
config_files = []
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
for i in [0, 1, 2]:
        server_configs.append((config_info) % (server_dirs[i], port_list[i], admin_list[i], ))
        config_files.append((os.path.join(os.path.join(CURR_DIR, 'conf-'+str(i+1)+'-mp'), 'zoo.cfg')))
        print config_files[i]
        with open(config_files[i], 'w') as f:
                f.write(server_configs[i])


# Start the ZooKeeper cluster
#for i in [0, 1, 2]:
        # chdir here so that zk can create the log here in this directory
#       os.chdir(server_dirs[i])
os.system(os.path.join(CURR_DIR, 'start-cluster-mp.sh '))
#os.chdir(CURR_DIR)

time.sleep(3)

out = ''
err = ''
#present_value = '0000'

all_start = True
# Get state of ZooKeeper nodes before reading data
if log_dir is not None:
        client_log_file = os.path.join(log_dir, 'log-client')
        with open(client_log_file, 'w') as f:
                f.write('Before workload\n')
                out, err = invoke_cmd('ps aux | grep zoo')
                to_write = ''
                out = out.split('\n')
                out = [i for i in out if i is not None and len(i) > 0 and ('conf-1-mp' in i or 'conf-2-mp' in i or 'conf-3-mp' in i)]
                to_check = ['conf-1-mp', 'conf-2-mp', 'conf-3-mp']
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


out = ''
err = ''

all_create = all_start
# Create Workload here
if all_start:
	for server_index in range(1, 4):
        	returned = None
        	zk = None

        	connect_string = host_list[server_index-1] + ':' + str(port_list[server_index-1])
        	kz_retry = KazooRetry(max_tries=1, delay=0.25, backoff=2)
        	zk = KazooClient(hosts=connect_string, connection_retry = kz_retry, command_retry = kz_retry, timeout = 1)
        	try:
                	zk.start()
                	for i in range(10):
                    		if i % 3 == (server_index-1):
                        		returned = zk.create("/zookeeper/" + str(i), 'a' * 4);
                	zk.stop()
                	out += 'Successfully create at server ' + str(server_index - 1) + '\n'
        	except Exception as e:
                	err += 'Could not create at server ' + str(server_index - 1) + '\t:' + str(e) + '\n'
			all_create = False


print out
print err

rerr = []
rout = []

# Issue Reads on all the nodes in the cluster and check its value
def read(server_index):  
        global rerr 
        global rout 
        returned = None
        zk = None

        connect_string = host_list[server_index-1] + ':' + str(port_list[server_index-1])
        kz_retry = KazooRetry(max_tries=1, delay=0.25, backoff=2)
        zk = KazooClient(hosts=connect_string, connection_retry = kz_retry, command_retry = kz_retry, timeout = 1)
        try:
                zk.start()
                for i in range(40):
                    returned, stat = zk.get("/zookeeper/" + str(random.randint(0,9)))
                zk.stop()
                returned = returned.strip().replace('\n', '')
                rout.append('Successful get at server ' + str(server_index - 1)) 
        except Exception as e:
                rerr.append('Could not get at server ' + str(server_index - 1) + '\t:' + str(e))




werr = []
wout= []

# Write workload
def write(server_index):
        global werr 
        global wout   
        returned = None
        zk = None

        connect_string = host_list[server_index-1] + ':' + str(port_list[server_index-1])
        kz_retry = KazooRetry(max_tries=1, delay=0.25, backoff=2)
        zk = KazooClient(hosts=connect_string, connection_retry = kz_retry, command_retry = kz_retry, timeout = 1)
        try:
                zk.start()
                for i in range(40):
                    returned = zk.set("/zookeeper/" + str(random.randint(0,9)), 'b' * 4)
                zk.stop()
                wout.append('Successfully put at server ' + str(server_index - 1))
        except Exception as e:
                werr.append('Could not put at server ' + str(server_index - 1) + '\t:' + str(e))

workloads = []
if all_create:
	for server_index in range(1, 4):
		buf = threading.Thread(target=lambda: read(server_index))
		buf.start()
		workloads.append(buf)
		buf = threading.Thread(target=lambda: write(server_index))
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
                out, err = invoke_cmd('ps aux | grep zoo')
                to_write = ''
                out = out.split('\n')
                out = [i for i in out if i is not None and len(i) > 0 and ('conf-1-mp' in i or 'conf-2-mp' in i or 'conf-3-mp' in i)]
                to_check = ['conf-1-mp', 'conf-2-mp', 'conf-3-mp']
                for check in to_check:
                        found = False
                        for i in out:
                                if check in i:
                                        found = True
                        to_write += check[:6] + ' running:' + str(found) + '\n'

                f.write(to_write)

time.sleep(3)
# Kill the ZooKeeper nodes
os.system("pkill -f \'java.*zoo*\'")
time.sleep(1)


#os.system("sudo chown -R $USER:$USER store*")

#for i in [0, 1, 2]:
#       os.system('rm -rf ' + config_files[i])

# if log_dir specified
if log_dir is not None:
        for i in range(0, len(server_dirs)):
                os.system('cp ' + os.path.join(os.path.join(CURR_DIR, 'logs-'+str(i+1)), zoo_logfile_name)  + ' ' + os.path.join(log_dir, 'log-'+str(i)))
