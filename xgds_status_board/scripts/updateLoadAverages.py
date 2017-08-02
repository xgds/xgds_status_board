#!/usr/bin/env python
import datetime
import os
import time
import logging
import json
import re
import threading


import django
django.setup()

from xgds_status_board.models import Subsystem, SubsystemStatus

COMMAND="uptime"

""" you have to have SSH keys set up for these to work.
"""

def setup(opts):
    with open(opts.configFile) as data_file:    
        data = json.load(data_file)
    data_file.close()
    if data:
        buildLoadAverageThreads(data)

def buildLoadAverageThreads(config):
    threads = []
    for name, values in config.iteritems():
        logging.info('BUILDING THREAD FOR ' + name)
        try: 
            subsystemStatus = SubsystemStatus(name)
            ssThread = threading.Thread(target=updateLoadAverage, name=name, args=(subsystemStatus, values['HOST']))
            threads.append(ssThread)
            ssThread.start()
        except:
            logging.error('invalid subsystem name %s '  % name)
        
    return threads

def getDefaultStatus(subsystemStatus):
    return {"name": subsystemStatus.name, 
            "displayName": subsystemStatus.displayName, 
            "elapsedTime": "",
            "statusColor": subsystemStatus.NO_DATA,
            "oneMin": "", 
            "fiveMin": "", 
            "lastUpdated": "",
            }

def updateLoadAverage(subsystemStatus, host):
    """ 
    updates the load average
    """
    logging.info("Running %s" % subsystemStatus.name)
    status = getDefaultStatus(subsystemStatus)
    while True: 
        result = subsystemStatus.runRemoteCommand(host, COMMAND)
        if result !=[]:
            loadStr = re.search('load average:(.*)\n', result[0]).group(1)
            loadTimes = loadStr.split(",")
            oneMin = float(loadTimes[0].strip())
            fiveMin = float(loadTimes[1].strip())
            lastUpdated = datetime.datetime.utcnow().isoformat()
            status['oneMin'] = oneMin
            status['fiveMin'] = fiveMin
            status['lastUpdated'] = lastUpdated
            # set it in memcache
            subsystemStatus.setStatus(status)
        else: 
            logging.error("Command %s in host %s returned []" % (COMMAND, host))
        time.sleep(60)
 

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-c', '--configFile',
                      default="",
                      help='full path to the config file with list of subsystems to ping')
    opts, _args = parser.parse_args()
    setup(opts)


if __name__ == '__main__':
    main()