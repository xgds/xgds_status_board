# __BEGIN_LICENSE__
#Copyright (c) 2015, United States Government, as represented by the 
#Administrator of the National Aeronautics and Space Administration. 
#All rights reserved.
#
#The xGDS platform is licensed under the Apache License, Version 2.0 
#(the "License"); you may not use this file except in compliance with the License. 
#You may obtain a copy of the License at 
#http://www.apache.org/licenses/LICENSE-2.0.
#
#Unless required by applicable law or agreed to in writing, software distributed 
#under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
#CONDITIONS OF ANY KIND, either express or implied. See the License for the 
#specific language governing permissions and limitations under the License.
# __END_LICENSE__

import datetime
import json
import subprocess
import traceback

from django.db import models
from django.conf import settings
from geocamUtil.modelJson import modelToDict
from xgds_core.models import Constant
from django.core.cache import caches  
from xgds_video.util import getSegmentPath
from geocamUtil.loader import LazyGetModelByName, getClassByName
from geocamUtil.datetimeJsonEncoder import DatetimeJsonEncoder


ACTIVE_FLIGHT_MODEL = LazyGetModelByName(settings.XGDS_PLANNER2_ACTIVE_FLIGHT_MODEL)
    

# pylint: disable=C1001

# Create your models here.
PRIORITY_CHOICES = (
    (0, '0'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
)


class SubsystemStatus():
    """ Uses Memcache to store status for subsystems so that status board can refer to it """
    
    OKAY = '#00ff00'
    WARNING = '#ffff00'
    ERROR = '#ff0000'
    NO_DATA = ''

    # get default
    # update one value of subsystem status
    # update subsystem status with json
    def __init__(self, subsystemName):
        self.cache = caches['default']
        self.subsystem = Subsystem.objects.get(name=subsystemName)
        self.name = self.subsystem.name
        self.displayName = self.subsystem.displayName
        if not self.cache.get(self.name):
            defaultStatus = self.getDefaultStatus()
            self.setStatus(defaultStatus)
    
    def getDefaultStatus(self):
        return {"name": self.name, 
                  "displayName": self.displayName, 
                  "elapsedTime": "",
                  "statusColor": self.NO_DATA,
                  "lastUpdated": "",
                  "flight": "" 
                  }
    
    def getStatus(self):
        try:
            return json.loads(self.cache.get(self.name))
        except:
            defaultStatus = self.getDefaultStatus()
            self.setStatus(defaultStatus)
            return defaultStatus
    
    def setStatus(self, statusJson):
        self.cache.set(self.name, json.dumps(statusJson, cls=DatetimeJsonEncoder))
    
    def getColorLevel(self, lastUpdated):
        """
        interval = (CurrentTime - LastUpdatedTime)
        compare interval to thresholds and return color level (OKAY,WARNING,ERROR)
        """
        if not lastUpdated:
            return self.ERROR
        currentTime = datetime.datetime.utcnow()
        elapsed = (currentTime - lastUpdated).total_seconds()
        if elapsed < self.subsystem.warningThreshold:
            return self.OKAY
        elif (elapsed < self.subsystem.failureThreshold) and (elapsed > self.subsystem.warningThreshold):
            return self.WARNING
        else: 
            return self.ERROR
        
    def getElapsedTimeSeconds(self, lastUpdated):
        if not lastUpdated:
            return ""
        currentTime = datetime.datetime.utcnow()
        return (currentTime - lastUpdated).total_seconds()
        
    def getElapsedTimeString (self, lastUpdated):
        elapsedSeconds = self.getElapsedTimeSeconds(lastUpdated)
        m, s = divmod(elapsedSeconds, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
        
    def runRemoteCommand(self, HOST, COMMAND):
        ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        return result


class StatusboardAnnouncement(models.Model):
    id = models.AutoField(primary_key=True)
    priority = models.IntegerField(null=True, blank=True,
                                   choices=PRIORITY_CHOICES,
                                   default=5,
                                   verbose_name='Priority (higher values are more important)')
    visible = models.BooleanField(null=False, blank=True, default=True)
    dateCreated = models.DateTimeField(null=True, db_column='dateCreated',
                                       blank=True, auto_now_add=True, editable=False)
    dateOfAnnouncement = models.DateTimeField(null=True, db_column='dateOfAnnouncement',
                                              blank=True)
    content = models.CharField(max_length=768, blank=True)

    class Meta:
        db_table = u'xgds_status_board_announcement'
        verbose_name = "Announcement"

    def __unicode__(self):
        return "%s: %s" % (self.dateCreated, self.content)


def midnightThisMorning():
    return datetime.datetime.utcnow().replace(hour=0, minute=0, second=0)


class StatusboardEvent(models.Model):
    id = models.AutoField(primary_key=True)
    priority = models.IntegerField(null=True, blank=True,
                                   choices=PRIORITY_CHOICES,
                                   default=5,
                                   verbose_name='Priority (higher values are more important)'
                                   )
    visible = models.BooleanField(null=False, blank=True, default=True)
    completed = models.BooleanField(null=False, blank=True, default=False)
    dateCreated = models.DateTimeField(null=True, db_column='dateCreated',
                                       blank=True, auto_now_add=True, editable=False)
    dateOfEvent = models.DateTimeField(null=True, db_column='dateOfEvent',
                                       blank=True, default=midnightThisMorning)
    content = models.CharField(max_length=768, blank=True)

    class Meta:
        db_table = u'xgds_status_board_event'
        verbose_name = "Event"

    def __unicode__(self):
        return "%s: %s" % (self.dateOfEvent, self.content)


class AbstractSubsystemGroup(models.Model):
    """
    EV1, EV2, Field Server, etc that groups subsystems in the monitor view.
    """
    name = models.CharField(max_length=128, blank=True, db_index=True, help_text='no spaces and unique')
    displayName = models.CharField(max_length=128, blank=True)
    warningThreshold = models.IntegerField(default=5, null=True, blank=True, help_text='in seconds')
    failureThreshold = models.IntegerField(default=10, null=True, blank=True, help_text='in seconds')
    
    class Meta:
        abstract = True
    
    def getTitle(self):
        return self.displayName
    
    def getIcon(self):
        pass
    
    def getStatus(self):
        pass
        
    def toDict(self):
        """
        Return a reduced dictionary that will be turned to JSON
        """
        result = modelToDict(self)
        return result
    
    def getSubsystemStatusList(self):
        result = []
        for subsystem in self.subsystems.all():
            try:  
                if subsystem.active:
                    subsystemStatus = subsystem.getStatus()
                    if subsystemStatus:
                        result.append(subsystemStatus)
            except: 
                continue
        return result
    
    def getSubsystemStatusListJson(self):
        result = self.getSubsystemStatusList()
        return json.dumps(result, sort_keys=True, cls=DatetimeJsonEncoder)


class SubsystemGroup(AbstractSubsystemGroup):
    def __unicode__(self):
        return "%s" % (self.name)


class AbstractSubsystem(models.Model):
    """
    Data quality, Video, etc. Each individual device.
    """
    name = models.CharField(max_length=128, blank=True, db_index=True, unique=True, help_text='no spaces and unique')
    displayName = models.CharField(max_length=128, blank=True)
    group = models.ForeignKey(SubsystemGroup, null=True, blank=True, related_name="subsystems")
    logFileUrl = models.CharField(max_length=512, blank=True)
    warningThreshold = models.IntegerField(default=5, null=True, blank=True, help_text='in seconds')
    failureThreshold = models.IntegerField(default=10, null=True, blank=True, help_text='in seconds')
    refreshRate = models.IntegerField(default=1, null=True, blank=True, help_text='in seconds')
    constantName = models.CharField(max_length=128, null=True, blank=True, help_text='constant name to look up the hostname')
    active = models.BooleanField(null=False, blank=True, default=True)

    def getTitle(self):
        return self.displayName
    
    def getHostname(self):
        """
        Returns the IP Address of the subsystem.
        """
        constant = Constant.objects.get(name = self.constantName)
        return constant.value

    def getStatus(self):
        try: 
            _cache = caches['default']
            return json.loads(_cache.get(self.name))
        except:
            subsystemStatus = SubsystemStatus(self.name)
            return subsystemStatus.getStatus()
                
    def toDict(self):
        """
        Return a reduced dictionary that will be turned to JSON
        """
        result = modelToDict(self)
        return result

    class Meta:
        abstract = True
        ordering = ['displayName']


class Subsystem(AbstractSubsystem):
    def __unicode__(self):
        return "%s" % (self.name)
