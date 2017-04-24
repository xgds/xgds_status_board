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

import logging

from datetime import datetime, timedelta
from pytz import timezone
import pytz
from apps.xgds_core.views import get_handlebars_templates
utc = pytz.utc

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from geocamUtil import anyjson as json
from geocamUtil.models.ExtrasDotField import convertToDotDictRecurse
from geocamUtil.loader import LazyGetModelByName

from xgds_status_board.models import StatusboardAnnouncement, StatusboardEvent, SubsystemGroup, Subsystem
from xgds_status_board import settings

from subprocess import Popen, PIPE
from time import sleep as time_sleep


# pylint: disable=E1101
default_timezone_offset = 0
XGDS_STATUS_BOARD_TEMPLATE_LIST = list(settings.XGDS_STATUS_BOARD_HANDLEBARS_DIR)
timezones = convertToDotDictRecurse(settings.STATUS_BOARD_TIMEZONES)


#print 'CALCULATING TIMEZONES WE HAVE %d' % len(timezones)
for timezone in timezones:
    timezone.tzobject = pytz.timezone(timezone.code)


def getMultiTimezones(time):
    """
    given a datetime that is in utc, return that time as the timezones defined in settings.
    """
    utc_time = utc.localize(time)
    return [(tz.name, utc_time.astimezone(tz.tzobject), tz.color)
            for tz in timezones]


def statusBoard(request):
    timestamp = datetime.utcnow()
    startTime = timestamp - timedelta(hours=12, microseconds=0)
    return render(request, 
                  "xgds_status_board/gdsStatusBoard.html",
                  {'STATUS_BOARD_TIMEZONES': settings.STATUS_BOARD_TIMEZONES,
                   'STATUS_BOARD_DATE_TIMEZONE': settings.STATUS_BOARD_DATE_TIMEZONE,
                   'navigation_tab': settings.STATUS_BOARD_VIEW_NAVIGATION_TAB,
                   'STATUS_BOARD_ANNOUNCEMENTS': settings.STATUS_BOARD_ANNOUNCEMENTS,
                   'STATUS_BOARD_SCHEDULE': settings.STATUS_BOARD_SCHEDULE,
                   'STATUS_BOARD_SCORE_SCHEDULE': settings.STATUS_BOARD_SCORE_SCHEDULE,
                   'SCORE_URL': settings.STATUS_BOARD_SCORE_URL,
                   'SCORE_START_TIME': startTime.isoformat(),
                   'TIMEZONE_OFFSET': default_timezone_offset
                   },
                  )


def statusBoardEdit(request):
    announcementList = StatusboardAnnouncement.objects.order_by('-priority')
    return render(request,
                  "xgds_status_board/EditAnnouncements.html",
                  {'announcements': announcementList,
                   'navigation_tab': settings.STATUS_BOARD_EDIT_NAVIGATION_TAB},
                  )


def statusBoardAnnouncements(request):
    announcementList = StatusboardAnnouncement.objects.\
        filter(visible=True).order_by('-dateCreated')
    result = []

    for announcement in announcementList:
        multiTimezones = getMultiTimezones(announcement.dateOfAnnouncement)
        announcement.time = [(t, color) for _name, t, color in multiTimezones]
        result.append(announcement)

    return render(request,
                  "xgds_status_board/announcements.html",
                  {'announcements': result}
                  )


def getAnnouncementTS(request):
    if request.is_ajax():
        annId = request.REQUEST['id']

        try:
            ann = StatusboardAnnouncement.objects.get(id=annId)
            return HttpResponse(str(ann.dateCreated))
        except StatusboardAnnouncement.DoesNotExist:
            return HttpResponse(status=500)


def addAnnouncement(request):
    if request.is_ajax():
        vis = bool(int(request.REQUEST['visible']))
        priority = request.REQUEST['priority']
        content = request.REQUEST['content']

        try:
            ann = StatusboardAnnouncement(priority=priority, visible=vis,
                                          content=content)
            ann.dateOfAnnouncement = datetime.utcnow()
            ann.save()
            return HttpResponse(str(ann.id))
        except Exception, e:  # pylint: disable=W0703
            logging.error(str(e))
            return HttpResponse("Error saving new announcement.", status=500)
    else:
        return HttpResponse(status=500)


def updateAnnouncement(request):
    if request.is_ajax():
        annId = request.REQUEST['id']
        value = request.REQUEST['value']
        colName = request.REQUEST['columnName']
        colPos = request.REQUEST['columnPosition']
        colId = request.REQUEST['columnId']
        rowId = request.REQUEST['rowId']
        logging.debug("got update event: annId=[%s] value=[%s] colName=[%s] colPos=[%s] colId=[%s] rowId=[%s]",
                      annId, value, colName, colPos, colId, rowId)

        ann = StatusboardAnnouncement.objects.get(id=annId)
        if colId == '1':
            ann.visible = bool(int(value))
        elif colId == '2':
            ann.priority = value
        elif colId == '3':
            ann.content = value

        ann.dateOfAnnouncement = datetime.utcnow()
        ann.save()
        return HttpResponse(value)
    else:
        return HttpResponse(status=500)


def deleteAnnouncement(request):
    if request.is_ajax():
        annId = request.REQUEST['id']

        try:
            ann = StatusboardAnnouncement.objects.get(id=annId)
        except StatusboardAnnouncement.DoesNotExist:
            return HttpResponse("Could not find announcement to delete. Please refresh the page.")

        try:
            ann.delete()
        except Exception:  # pylint: disable=W0703
            return HttpResponse("Server error attempting to delete announcement.")

        return HttpResponse("ok")
    else:
        return HttpResponse(status=500)


def statusBoardAnnouncementsJSON(request):
    announcementList = StatusboardAnnouncement.objects.\
        filter(visible=True).order_by('-dateCreated')
    jsonList = []
    for announcement in announcementList:
        jsonList.append({'id': announcement.id,
                         'priority': announcement.priority,
                         'visible': announcement.visible,
                         'dateCreated': announcement.dateCreated.isoformat() + 'Z',
                         'content': announcement.content,
                         'utcDateCreated': announcement.dateOfAnnouncement.isoformat() + 'Z',
                         })
    stuff = json.dumps(jsonList)
    return HttpResponse(stuff, content_type='text/plain')


# TODO support timezone array
def statusBoardSchedule(request):
    eventList = StatusboardEvent.objects.\
        filter(visible=True).filter(completed=False).order_by('dateOfEvent')
    #siteTimeOffset = datetime.timedelta(hours = settings.REMOTE_TIMEZONE_OFFSET)
    localTimes = [e.dateOfEvent.strftime("%m/%d/%Y %H:%M:%S")
                  for e in eventList]
    siteTimeOffset = 0
    siteTimes = [e.dateOfEvent + siteTimeOffset for e in eventList]
    eventsPlusSiteTimes = zip(eventList, siteTimes)
    schedHtml = render(request,
                       "xgds_status_board/schedule.html",
                       {'eventList': eventList,
                        'eventsPlusSiteTimes': eventsPlusSiteTimes,
                        'STATUS_BOARD_TIMEZONES': settings.STATUS_BOARD_TIMEZONES,
                        'STATUS_BOARD_DATE_TIMEZONE': settings.STATUS_BOARD_DATE_TIMEZONE,
                        })
    resultDict = {'schedHtml': schedHtml.content, 'localTimes': localTimes,
                  'dateCount': eventList.count()}
    resultJson = json.dumps(resultDict)
    resp = HttpResponse(resultJson, content_type='application/json')

    return resp


def getServerDatetimeJSON(request):
    timestamp = datetime.utcnow()
    times = getMultiTimezones(timestamp)
    result = []
    for name, time, _color in times:
        datedict = {'dayName': time.strftime("%a"),
                    'monthName': time.strftime("%b"),
                    'month': time.month,
                    'day': time.day,
                    'year': time.year,
                    'shortyear': timestamp.strftime("%y"),
                    'hour': time.strftime("%H"),
                    'hour12': time.strftime("%I"),
                    'ampm': time.strftime("%p"),
                    'min': time.strftime("%M"),
                    'sec': time.strftime("%S"),
                    'zone': name}
        result.append(datedict)
    datejson = json.dumps(result)
    return HttpResponse(datejson, content_type='application/json')


def getSubsystemGroupJson():
    # gets the json of all active subsystems
    subsystemStatusDict = {}
    subsystemGroups = SubsystemGroup.objects.all()
    for subsystemGroup in subsystemGroups:
        subsystemStatusDict[subsystemGroup.name] = []
        subsystems = Subsystem.objects.filter(group = subsystemGroup)
        for subsystem in subsystems:
            if subsystem.active:
                try:  
                    subsystemStatus = subsystem.getStatus()
                except: 
                    continue
                if subsystemStatus:
                    subsystemStatusDict[subsystemGroup.name].append(subsystemStatus)
    subsystemStatusJson = json.dumps(subsystemStatusDict, indent=4, sort_keys=True)
    return subsystemStatusJson


def showSubsystemStatus(request):
    subsystemStatusJson = getSubsystemGroupJson()
    return render(request,
                  "xgds_status_board/subsystemStatus.html",
                  {'templates': get_handlebars_templates(XGDS_STATUS_BOARD_TEMPLATE_LIST, 'XGDS_STATUS_BOARD_TEMPLATE_LIST'),
                   'subsystemStatusJson': subsystemStatusJson,
                   'XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL': reverse('xgds_status_board_subsystemStatusJson')},
                  )


def subsystemStatusJson(request):
    subsystemStatusJson = getSubsystemGroupJson()
    return HttpResponse(subsystemStatusJson, 
                        content_type='application/json')