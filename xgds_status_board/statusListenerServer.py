#!/usr/bin/python

import datetime

import Pyro.core
from django.core.exceptions import ObjectDoesNotExist

from share2.shareCore.utils import anyjson as json
from gds.statusBoard.models import StatusboardPlanStatus

class TestServer(Pyro.core.ObjBase):
    def __init__(self):
        self.data = []
        # Initialize Pyro
        Pyro.core.ObjBase.__init__(self)

    def submitData(self,jstr):
        # Print what we got
        print 'got data:'
        print jstr
        obj = json.loads(jstr)
        # for now, assume it's plan status, that's all we have...
        planStat = obj['planStatus']
        for k in planStat.keys():
            if k != 'timestamp':
                try:
                    statusInfo = StatusboardPlanStatus.objects.get(keyword = k)
                    statusInfo.value = json.dumps(planStat[k])
                    statusInfo.timestamp = \
                        datetime.datetime.\
                        fromtimestamp(float(planStat['timestamp']))
                    statusInfo.save()
                except ObjectDoesNotExist:
                    StatusboardPlanStatus.objects.\
                        create(timestamp = datetime.datetime.\
                                   fromtimestamp(float(planStat['timestamp'])),
                               keyword = k,
                               value = json.dumps(planStat[k]))

    # Prints all the data we got so far
    def printData(self):
        for d in self.data:
            print d

    # Returns all the data we got so far
    def getData(self):
        return self.data

Pyro.core.initServer()
daemon=Pyro.core.Daemon(port=7766)
uri=daemon.connect(TestServer(),"TestServer")

print "The daemon runs on port:",daemon.port
print "The object's uri is:",uri

daemon.requestLoop()
