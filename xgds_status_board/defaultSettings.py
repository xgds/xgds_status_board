# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

"""
This app may define some new parameters that can be modified in the
Django settings module.  Let's say one such parameter is FOO.  The
default value for FOO is defined in this file, like this:

  FOO = 'my default value'

If the admin for the site doesn't like the default value, they can
override it in the site-level settings module, like this:

  FOO = 'a better value'

Other modules can access the value of FOO like this:

  from xgds_status_board import settings
  print settings.FOO

Don't try to get the value of FOO from django.conf.settings.  That
settings object will not know about the default value!
"""

# this can be used to specify a string in your template to indicate a navigation tab.  It is not required.
STATUS_BOARD_VIEW_NAVIGATION_TAB = 'status.view'
STATUS_BOARD_EDIT_NAVIGATION_TAB = 'status.edit'

SCORE_URL = 'https://techno.arc.nasa.gov/DRATS/schedule.json'

STATUS_BOARD_ANNOUNCEMENTS = True
STATUS_BOARD_SCHEDULE = False
STATUS_BOARD_SCORE_SCHEDULE = True

# to add timezones to the status board display fill out this handy list.
# in the database things are stored in uct (GMT)
# this is the order of display
# if you want MORE than 3 timezones you will have to edit the css and create time classes for the colors.
# right now we are only using the 2nd thing, ie US/Central -- but may want to use the others in javascript
STATUS_BOARD_TIMEZONES = []
STATUS_BOARD_TIMEZONES.append(('GMT','Etc/Greenwich'))
STATUS_BOARD_TIMEZONES.append(('CDT', 'US/Central')) 
STATUS_BOARD_TIMEZONES.append(('MST', 'US/Mountain'))
#STATUS_BOARD_TIMEZONES.append(('EST', 'US/Eastern'))
#STATUS_BOARD_TIMEZONES.append(('PDT', 'US/Pacific')) 

# this is the index of the timezone above to use for the date (count from 0)
# this will control when events will roll over, ie when status board lists will no longer display things for the current day
STATUS_BOARD_DATE_TIMEZONE = 2 


