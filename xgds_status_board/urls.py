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
    (r'^announcements.html$', views.statusBoardAnnouncements),
    (r'^announcementsJSON$', views.statusBoardAnnouncementsJSON,
     {'readOnly':True}),
    (r'^schedule.json$', views.statusBoardSchedule),
    (r'^serverDatetime.json$', views.getServerDatetimeJSON),
    url(r'^edit', views.statusBoardEdit, name='xgds_status_boardEdit')
)
