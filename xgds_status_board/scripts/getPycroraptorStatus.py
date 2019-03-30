#!/usr/bin/env python

from django.conf import settings
import json
import zerorpc

class PycroraptorStatus:
    def __init__(self):
        self.port = self.getRpcPort()
        self.client = zerorpc.Client(timeout=1000)
        self.client.connect(self.port)

    def getRpcPort(self):
        clientName = 'pyraptord'
        ports = json.loads(file(settings.ZEROMQ_PORTS, 'r').read())
        rpcPort = ports[clientName]['rpc']
        return rpcPort

    def getListOfProcesses(self):
        client = zerorpc.Client(self.port)
        serviceConfig = client.getConfig('SERVICES')
        status = client.getStatusAll()
        client.disconnect(self.port)
        configItems = serviceConfig.items()
        processes = {}
        for name, _ in configItems:
            procStatus = status.get(name, {'status': 'notStarted'})['status']
            processes[name] = procStatus
        return processes