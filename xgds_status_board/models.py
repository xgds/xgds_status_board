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

from django.db import models
from geocamUtil.modelJson import modelToDict
from xgds_core.models import Constant
from django.core.cache import caches  

#subsystem status markers
OKAY = 1
WARNING = 2
ERROR = 3

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
    
    def getColor(self):
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

    class Meta:
        abstract = True
    
    def getTitle(self):
        return self.displayName
    
    def getStatus(self):
        # this might be a data quality: 
        if (self.name == 'gpsDataQuality1') or (self.name == 'gpsDataQuality2'):
            return _cache.get(self.name)
        else:
            lastUpdated = _cache.get(self.name)
            if not lastUpdated:
                return ERROR
            currentTime = datetime.datetime.utcnow()
            elapsed = (currentTime - lastUpdated).total_seconds()
            if elapsed < self.warningThreshold:
                return OKAY
            elif (elapsed < self.failureThreshold) and (elapsed > self.warningThreshold):
                return WARNING
            else: 
                return ERROR
        
            
    def getConstantName(self):
        """
        Name of the 'Constant' object under which this subsystem is stored. 
        """
        if self.name == 'gpsController1': 
            return 'EV1_TRACKING_IP'
        elif self.name == 'gpsController2':
            return 'EV2_TRACKING_IP'
        elif self.name == 'redCamera': 
            return 'RED_CAMERA_IP'
        elif self.name == 'FTIR': 
            return 'FTIR_IP'
        elif self.name == 'video1':
            return 'EV1_CAMERA_IP'
        elif self.name == 'video2':
            return 'EV2_CAMERA_IP'
        elif self.name == 'saCamera':
            return 'SA_CAMERA_IP'
    
    def getHostname(self):
        """
        Returns the IP Address of the subsystem.
        """
        constant = Constant.objects.get(name = self.getConstantName())
        return constant.value
    
    def getColor(self):
        if self.getStatus() == OKAY:
            return '#00ff00'
        elif self.getStatus() == WARNING:
            return '#ffff00'
        else: 
            return '#ff0000'
    
    def getStatusJson(self):
        try: 
            lastUpdated = _cache.get(self.name).strftime('%Y-%m-%d %H:%M:%S')
        except: 
            lastUpdated = ""
        json = {"name": self.name,
                "statusColor": self.getColor(),
                "lastUpdated": lastUpdated}
        return json

    
    def toDict(self):
        """
        Return a reduced dictionary that will be turned to JSON
        """
        result = modelToDict(self)
        return result
    

class Subsystem(AbstractSubsystem):
    pass