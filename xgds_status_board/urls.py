# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

from xgds_status_board import views

urlpatterns = patterns(
    '',
    url(r'^$', views.statusBoard, name='xgds_status_boardView'),
    (r'^announcements.html$', views.statusBoardAnnouncements, {'readOnly':True,
                                                    'loginRequired': False}, "announcements.html"),
    (r'^announcementsJSON$', views.statusBoardAnnouncementsJSON,{'readOnly':True,
                                                    'loginRequired': False}),
    (r'^schedule.json$', views.statusBoardSchedule, {'readOnly':True,
                                                    'loginRequired': False}, "schedule.json"),
    (r'^serverDatetime.json$', views.getServerDatetimeJSON, {'readOnly':True,
                                                    'loginRequired': False}, "serverDatetime.json"),
    (r'^edit/', views.statusBoardEdit, {}, "xgds_status_boardEdit"),
    (r'^addAnnouncement$', views.addAnnouncement, {}, "addAnnouncement"),
    (r'^updateAnnouncement$', views.updateAnnouncement, {}, "updateAnnouncement"),
    (r'^deleteAnnouncement$', views.deleteAnnouncement, {}, "deleteAnnouncement"),
    (r'^getAnnouncementTS$', views.getAnnouncementTS, {'readOnly':True,
                                                    'loginRequired': False}, "getAnnouncementTS"),
)
