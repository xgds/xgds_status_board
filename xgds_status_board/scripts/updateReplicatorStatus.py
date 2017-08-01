#!/usr/bin/env python
import datetime
import os
import time
import memcache
import logging
import json
import dateutil.parser

import django
django.setup()

from xgds_status_board.models import Subsystem, SubsystemStatus


def setReplicatorStatus(opts):
    """
    Check each tungsten replicator for replication status for a response at every "interval_sec" seconds.
    """
    subsystemName = opts.subsystemName
    HOST = opts.host
    COMMAND = opts.command
    
    try: 
        subsystemStatus = SubsystemStatus(subsystemName)
    except:
        logging.error('invalid subsystem name')
        return 
    
    while True: 
        result = subsystemStatus.runRemoteCommand(HOST, COMMAND)
        statusColor = subsystemStatus.OKAY
        if result !=[]:
            for line in result:
                if "state" in line: 
                    state = line.replace(" ", "").split(':')[1]
                    if not ("ONLINE" in state):
                        statusColor = subsystemStatus.ERROR
                        continue
        else: # result is empty
            statusColor = subsystemStatus.NO_DATA

        status = subsystemStatus.getStatus()
        lastUpdated = dateutil.parser.parse(status['lastUpdated'])
        elapsedTimeString = subsystemStatus.getElapsedTimeString(lastUpdated)
        status['statusColor'] = statusColor
        status['elapsedTime'] = elapsedTimeString
        status['lastUpdated'] = datetime.datetime.utcnow().isoformat()
        subsystemStatus.setStatus(status)
        seconds = subsystemStatus.subsystem.refreshRate
        time.sleep(seconds)

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-n', '--subsystemName',
                      default="",
                      help='name of the subsystem to ping')
    parser.add_option('-h', '--host',
                      default="irg@boat",
                      help='user@machine')
    parser.add_option('-c', '--command',
                      default='/home/irg/tungsten/tungsten/tungsten-replicator/bin/trepctl services',
                      help='path to trepctl services for tungsten')
    opts, _args = parser.parse_args()
    setReplicatorStatus(opts)


if __name__ == '__main__':
    main()
