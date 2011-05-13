# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    
    (r'^$', views.statusBoard),
    (r'^announcements.html$', views.statusBoardAnnouncements),
    (r'^schedule.json$', views.statusBoardSchedule),
    (r'^serverDatetime.json$', views.getServerDatetimeJSON),
)
