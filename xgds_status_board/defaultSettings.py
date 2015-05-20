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

STATUS_BOARD_SCORE_URL = 'please_set_score_url_in_siteSettings.py'

STATUS_BOARD_ANNOUNCEMENTS = True
STATUS_BOARD_SCHEDULE = False
STATUS_BOARD_SCORE_SCHEDULE = True

# to add timezones to the status board display override these values *** in siteSettings.py ***
# note: in the database things are stored in UTC (GMT)
GMT_TIME_ZONE = {'name': 'GMT',
                 'code': 'Etc/UTC',
                 'color': '#304073'}
STATUS_BOARD_TIMEZONES = [GMT_TIME_ZONE]

# this is the timezone to use for the date this will control when events
# will roll over, ie when status board lists will no longer display
# things for the current day
STATUS_BOARD_DATE_TIMEZONE = GMT_TIME_ZONE

# include this in your siteSettings.py BOWER_INSTALLED_APPS
STATUS_BOARD_BOWER_INSTALLED_APPS = (
    'jquery-countdown',
    'jquery-timers=https://sparqlpush.googlecode.com/svn-history/r2/trunk/client/jquery.timers-1.2.js',
    'datatables-editable=https://github.com/jphustman/jquery-datatables-editable.git'
)
