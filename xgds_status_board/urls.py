# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls import patterns

from xgds_status_board import views

urlpatterns = patterns(
    '',
    (r'^$', views.statusBoard, {'readOnly': True},
     'xgds_status_boardView'),
    (r'^announcements$', views.statusBoardAnnouncements, {'readOnly': True},
     "announcements"),
    (r'^announcementsJSON$', views.statusBoardAnnouncementsJSON, {'readOnly': True}),
    (r'^schedule.json$', views.statusBoardSchedule, {'readOnly': True}, "schedule.json"),
    (r'^serverDatetime.json$', views.getServerDatetimeJSON, {'readOnly': True}, "serverDatetime.json"),
    (r'^edit/', views.statusBoardEdit, {}, "xgds_status_boardEdit"),
    (r'^addAnnouncement$', views.addAnnouncement, {}, "addAnnouncement"),
    (r'^updateAnnouncement$', views.updateAnnouncement, {}, "updateAnnouncement"),
    (r'^deleteAnnouncement$', views.deleteAnnouncement, {}, "deleteAnnouncement"),
    (r'^getAnnouncementTS$', views.getAnnouncementTS, {'readOnly': True}, "getAnnouncementTS"),
)
