# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib import admin

from xgds_status_board.models import *

class StatusboardAnnouncementAdmin(admin.ModelAdmin):
    fields = ['content', 'priority', 'visible']

class StatusboardEventAdmin(admin.ModelAdmin):
    fields = ['dateOfEvent', 'content', 'priority',
              'visible', 'completed',
              ]

admin.site.register(StatusboardAnnouncement, StatusboardAnnouncementAdmin)
admin.site.register(StatusboardEvent, StatusboardEventAdmin)
