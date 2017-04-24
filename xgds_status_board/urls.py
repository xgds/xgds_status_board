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

urlpatterns = [
    url(r'^$', views.statusBoard, {'readOnly': True}, 'xgds_status_boardView'),
    url(r'^announcements$', views.statusBoardAnnouncements, {'readOnly': True},
     "announcements"),
    url(r'^announcementsJSON$', views.statusBoardAnnouncementsJSON, {'readOnly': True}),
    url(r'^schedule.json$', views.statusBoardSchedule, {'readOnly': True}, "schedule.json"),
    url(r'^serverDatetime.json$', views.getServerDatetimeJSON, {'readOnly': True}, "serverDatetime.json"),
    url(r'^edit/', views.statusBoardEdit, {}, "xgds_status_boardEdit"),
    url(r'^addAnnouncement$', views.addAnnouncement, {}, "addAnnouncement"),
    url(r'^updateAnnouncement$', views.updateAnnouncement, {}, "updateAnnouncement"),
    url(r'^deleteAnnouncement$', views.deleteAnnouncement, {}, "deleteAnnouncement"),
    url(r'^getAnnouncementTS$', views.getAnnouncementTS, {'readOnly': True}, "getAnnouncementTS"),
    url(r'^subsystemStatus/$', views.showSubsystemStatus, {'loginRequired': False}, 'xgds_status_board_showSubsystemStatus'),
    url(r'^subsystemStatus\.json$', views.subsystemStatusJson, {}, 'xgds_status_board_subsystemStatusJson')
]
