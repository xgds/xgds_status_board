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

from django.conf.urls import url

from xgds_status_board import views

urlpatterns = [url(r'^announcementsJSON$', views.statusBoardAnnouncementsJSON),
               url(r'^schedule.json$', views.statusBoardSchedule, {}, "schedule.json"),
               url(r'^serverDatetime.json$', views.getServerDatetimeJSON, {}, "serverDatetime.json"),
               url(r'^getAnnouncementTS$', views.getAnnouncementTS, {}, "getAnnouncementTS"),
               url(r'^subsystemStatusJson/(?P<groupName>\w*)$', views.subsystemStatusJson, {}, 'xgds_status_board_subsystemStatusJson'),
               url(r'^multiSubsystemStatusJson/$', views.multiSubsystemStatusJson, {}, 'xgds_status_board_multiSubsystemStatusJson'),
               url(r'^processListJson$', views.pycroraptorProcessListJson, {}, 'xgds_status_board_pycroraptorProcessListJson'),
               url(r'^persistentErrors$', views.persistentErrorsListJson, {}, 'xgds_status_board_persistentErrorsListJson'),
               url(r'^deleteError$', views.persistentErrorsDelete, {}, 'xgds_status_board_persistentErrorsDelete'),
               ]
