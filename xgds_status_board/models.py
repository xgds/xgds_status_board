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
import dateutil.parser

from django.db import models
from geocamUtil.modelJson import modelToDict
from xgds_core.models import Constant
from django.core.cache import caches  

#subsystem status markers
OKAY = '#00ff00'
WARNING = '#ffff00'
ERROR = '#ff0000'
    

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

_cache = caches['default']

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
    content = models.CharField(max_length=765, blank=True)

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
    content = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = u'xgds_status_board_event'
        verbose_name = "Event"

    def __unicode__(self):
        return "%s: %s" % (self.dateOfEvent, self.content)


class AbstractSubsystemGroup(models.Model):
    """
    EV1, EV2, Field Server, etc that groups subsystems in the monitor view.
    """
    name = models.CharField(max_length=255, blank=True, help_text='no spaces and unique')
    displayName = models.CharField(max_length=255, blank=True)
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


class SubsystemGroup(AbstractSubsystemGroup):
    pass


class AbstractSubsystem(models.Model):
    """
    Data quality, Video, etc. Each individual device.
    """
    name = models.CharField(max_length=255, blank=True, help_text='no spaces and unique')
    displayName = models.CharField(max_length=255, blank=True)
    group = models.ForeignKey(SubsystemGroup, null=True, blank=True, related_name="subsystems")
    logFileUrl = models.CharField(max_length=765, blank=True)
    warningThreshold = models.IntegerField(default=5, null=True, blank=True, help_text='in seconds')
    failureThreshold = models.IntegerField(default=10, null=True, blank=True, help_text='in seconds')
    refreshRate = models.IntegerField(default=1000, null=True, blank=True, help_text='in miliseconds')
    constantName = models.CharField(max_length=255, null=True, blank=True, help_text='constant name to look up the hostname')

    class Meta:
        abstract = True
    
    def getTitle(self):
        return self.displayName
    
    def getHostname(self):
        """
        Returns the IP Address of the subsystem.
        """
        constant = Constant.objects.get(name = self.constantName)
        return constant.value
    
    def getElapsedSeconds(self, lastUpdated):
        currentTime = datetime.datetime.utcnow()
        elapsed = (currentTime - lastUpdated).total_seconds()
        return elapsed
    
    def getElapsedTimeString(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
    
    def getColorLevel(self, lastUpdated):
        """
        interval = (CurrenTime - LastUpdatedTime)
        compare interval to thresholds and return color level (OKAY,WARNING,ERROR)
        """
        if not lastUpdated:
            return ERROR
        elapsed = self.getElapsedSeconds(lastUpdated)
        if elapsed < self.warningThreshold:
            return OKAY
        elif (elapsed < self.failureThreshold) and (elapsed > self.warningThreshold):
            return WARNING
        else: 
            return ERROR
    
    def getLoadAverage(self):
        subsystemStatus = _cache.get(self.name)
        noData = {'name': self.name,
                  'oneMin': 'no data',
                  'fiveMin': 'no data',
                  'elapsedTime': ''}
        if subsystemStatus is None:
            return noData
        try: 
            jsonDict = json.loads(subsystemStatus)
        except: 
            return noData
        timestampString = jsonDict['lastUpdated']
        lastUpdated = dateutil.parser.parse(timestampString)
        elapsedSeconds = self.getElapsedSeconds(lastUpdated)
        elapsedTimeStr = self.getElapsedTimeString(elapsedSeconds)
        retval = {'name': self.name,
                  'oneMin': jsonDict['oneMin'], 
                  'fiveMin': jsonDict['fiveMin'],
                  'elapsedTime': elapsedTimeStr}
        return retval
    
    def getDataQuality(self):
        subsystemStatus = _cache.get(self.name)
        noData = {'name': self.name,
                  'statusColor': ERROR,
                  'elapsedTime': ''}
        if subsystemStatus is None:
            return noData
        try: 
            jsonDict = json.loads(subsystemStatus)
        except: 
            return noData
        timestampString = jsonDict['lastUpdated']
        lastUpdated = dateutil.parser.parse(timestampString)
        elapsedSeconds = self.getElapsedSeconds(lastUpdated)
        elapsedTimeStr = self.getElapsedTimeString(elapsedSeconds)
        retval ={'name': self.name,
                 'statusColor': jsonDict['dataQuality'],
                 'elapsedTime': elapsedTimeStr}
        return retval
    
    def getStatus(self):
        subsystemName = self.name
        subsystemStatus = _cache.get(subsystemName)
        noData = {'name': subsystemName,
                  'statusColor': ERROR,
                  'elapsedTime': ''}
        if subsystemStatus is None:
            return noData
        try: 
            jsonDict = json.loads(subsystemStatus)
        except: 
            return noData
        timestampString = jsonDict['lastUpdated']
        lastUpdated = dateutil.parser.parse(timestampString)
        elapsedSeconds = self.getElapsedSeconds(lastUpdated)
        elapsedTimeStr = self.getElapsedTimeString(elapsedSeconds)
        level = self.getColorLevel(lastUpdated)
        retval = {'name': subsystemName,
                  'statusColor': level, 
                  'elapsedTime': elapsedTimeStr}
        return retval
                
    def toDict(self):
        """
        Return a reduced dictionary that will be turned to JSON
        """
        result = modelToDict(self)
        return result
    

class Subsystem(AbstractSubsystem):
    pass