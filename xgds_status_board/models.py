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

#
# Note -- was intended for K10 plan status monitoring.  Should probably
# be moved to Kn specific repository.
#
# class StatusboardPlanStatus(models.Model):
#     id = models.IntegerField(primary_key=True)
#     timestamp = models.DateTimeField(null=True)
#     keyword = models.CharField(max_length=64, blank=True)
#     value = models.CharField(max_length=196, blank=True)
#     class Meta:
#         db_table = u'StatusBoard_Plan_Status'
#         verbose_name = "PlanStatus"
#     def __unicode__(self):
#         return "%s: %s (%s)" % (self.keyword, self.value, self.timestamp)
