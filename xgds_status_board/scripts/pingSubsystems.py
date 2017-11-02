#!/usr/bin/env python
#__BEGIN_LICENSE__
# Copyright (c) 2015, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All rights reserved.
#
# The xGDS platform is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#__END_LICENSE__
import datetime
import os
import time
import threading
import logging
import json

import django
django.setup()

from xgds_status_board.models import SubsystemStatus
from xgds_status_board.util import *

def setup(opts):
    with open(opts.configFile) as data_file:    
        data = json.load(data_file)
    data_file.close()
    if data:
        buildPingThreads(data)
        
def buildPingThreads(config):
    threads = []
    for subsystem in config:
        try: 
            subsystemStatus = SubsystemStatus(subsystem)
            ssThread = threading.Thread(target=setSubsystemStatus, name=subsystem, args=[subsystemStatus])
            threads.append(ssThread)
            ssThread.start()
        except:
            logging.error('invalid subsystem name %s '  % subsystem)
        
    return threads

def getDefaultStatus(subsystemStatus):
    return {"name": subsystemStatus.name, 
            "displayName": subsystemStatus.displayName, 
            "refreshRate": subsystemStatus.subsystem.refreshRate,
            "lastUpdated": "",
            }

def setSubsystemStatus(subsystemStatus):
    """
    Pings each subsystem for a response at every "interval_sec" seconds.
    """
    hostname = subsystemStatus.subsystem.getHostname()
    status = getDefaultStatus(subsystemStatus)
    lastUpdated = datetime.datetime.utcnow()
    status['lastUpdated'] = lastUpdated
    while hostname:

        seconds = subsystemStatus.subsystem.refreshRate
        status['refreshRate'] =  subsystemStatus.subsystem.refreshRate
        
        response = os.system("ping -c 1 " + hostname)
        if response != 0: # cannot ping host
            # try pinging again.
            response = os.system("ping -c 1 " + hostname)
        if response == 0: # hostname is up
            lastUpdated = datetime.datetime.utcnow()
            status['lastUpdated'] = lastUpdated.isoformat()
            status['statusColor'] = OKAY_COLOR
        else:
            status['statusColor'] = ERROR_COLOR
            
        # this sets the memcache
        subsystemStatus.setStatus(status)
        time.sleep(seconds)

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
