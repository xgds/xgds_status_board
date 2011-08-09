# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import logging

from datetime import datetime
from pytz import timezone
import pytz
utc = pytz.utc

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import  HttpResponse

from geocamUtil import anyjson as json

from xgds_status_board.models import StatusboardAnnouncement, StatusboardEvent
from xgds_status_board import settings

timezones = []
for tzinfo in settings.STATUS_BOARD_TIMEZONES:
    zone = timezone(tzinfo[1])
    timezones.append(zone)

today_timeclass = 'time%d' % (settings.STATUS_BOARD_DATE_TIMEZONE + 1);
        
# given a datetime that is in utc, return that time as the timezones defined in settings.        
def getMultiTimezones(time):
    utc_time = utc.localize(time)
    result = []
    for tz in timezones:
        result.append(utc_time.astimezone(tz))
    return result
    
def statusBoard(request):
    return render_to_response("xgds_status_board/gdsStatusBoard.html",
                              {'STATUS_BOARD_TIMEZONES': settings.STATUS_BOARD_TIMEZONES,
                               'STATUS_BOARD_DATE_TIMEZONE_INDEX': settings.STATUS_BOARD_DATE_TIMEZONE,
                               'today_timeclass': today_timeclass,
                               'navigation_tab':settings.STATUS_BOARD_VIEW_NAVIGATION_TAB,
                               'STATUS_BOARD_ANNOUNCEMENTS': settings.STATUS_BOARD_ANNOUNCEMENTS,
                               'STATUS_BOARD_SCHEDULE': settings.STATUS_BOARD_SCHEDULE,
                               'STATUS_BOARD_SCORE_SCHEDULE': settings.STATUS_BOARD_SCORE_SCHEDULE,
                               'SCORE_URL':settings.SCORE_URL,
                              },
                              context_instance=RequestContext(request))

def statusBoardEdit(request):
    announcementList = StatusboardAnnouncement.objects.\
        order_by('-priority')
    return render_to_response("xgds_status_board/EditAnnouncements.html", 
                              {'announcements': announcementList,
                               'navigation_tab':settings.STATUS_BOARD_EDIT_NAVIGATION_TAB,},
                              context_instance=RequestContext(request))
    
    
def statusBoardAnnouncements(request):
    announcementList = StatusboardAnnouncement.objects.\
        filter(visible=True).order_by('-dateCreated')
    result = []
        
    for announcement in announcementList:
        announcement.time = getMultiTimezones(announcement.dateOfAnnouncement)
        result.append(announcement)
        
    return render_to_response("xgds_status_board/announcements.html", 
                              {'announcements': result,
                               'STATUS_BOARD_DATE_TIMEZONE_INDEX': settings.STATUS_BOARD_DATE_TIMEZONE,
                               'today_timeclass': today_timeclass,
                               'STATUS_BOARD_TIMEZONES': settings.STATUS_BOARD_TIMEZONES,
                               'STATUS_BOARD_DATE_TIMEZONE': timezones[settings.STATUS_BOARD_DATE_TIMEZONE]},
                              context_instance=RequestContext(request))

def getAnnouncementTS(request):
    if request.is_ajax():
        id = request.REQUEST['id']

        try:
            ann = StatusboardAnnouncement.objects.get(id=id)
            return HttpResponse(str(ann.dateCreated))
        except StatusboardAnnouncement.DoesNotExist:
            return HttpResponse(status=500)
        

def addAnnouncement(request):
    if request.is_ajax():
        vis = bool(int(request.REQUEST['visible']))
        priority = request.REQUEST['priority']
        content = request.REQUEST['content']

        try:
            ann = StatusboardAnnouncement(priority=priority, visible=vis,content=content)
            ann.dateOfAnnouncement = datetime.utcnow()
            ann.save()
            return HttpResponse(str(ann.id))
        except Exception, e:
            logging.error(str(e))
            return HttpResponse("Error saving new announcement.", status=500)
    else:
        return HttpResponse(status=500)

def updateAnnouncement(request):
    if request.is_ajax():
        id = request.REQUEST['id']
        value = request.REQUEST['value']
        colName = request.REQUEST['columnName']
        colPos = request.REQUEST['columnPosition']
        colId = request.REQUEST['columnId']
        rowId = request.REQUEST['rowId']
        logging.debug("got update event: id=[%s] value=[%s] colName=[%s] colPos=[%s] colId=[%s] rowId=[%s]"%(id, value, colName, colPos, colId, rowId))

        ann = StatusboardAnnouncement.objects.get(id=id)
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
        id = request.REQUEST['id']

        try:
            ann = StatusboardAnnouncement.objects.get(id=id)
        except StatusboardAnnouncement.DoesNotExist:
            return HttpResponse("Could not find announcement to delete. Please refresh the page.")

        try:
            ann.delete()
        except Exception:
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
                         'dateCreated':announcement.dateCreated.isoformat()+'Z',
                         'content': announcement.content,
                         'utcDateCreated': announcement.dateOfAnnouncement.isoFormat()+'Z',
                         })
       
    stuff = json.dumps(jsonList)
    return HttpResponse(stuff, mimetype='text/plain')

#TODO support timezone array
def statusBoardSchedule(request):
    eventList = StatusboardEvent.objects.\
        filter(visible=True).filter(completed=False).order_by('dateOfEvent')
    #siteTimeOffset = datetime.timedelta(hours = settings.REMOTE_TIMEZONE_OFFSET)
    localTimes = [e.dateOfEvent.strftime("%m/%d/%Y %H:%M:%S") 
                  for e in eventList]
    siteTimeOffset = 0
    siteTimes = [e.dateOfEvent + siteTimeOffset for e in eventList]
    eventsPlusSiteTimes = zip(eventList, siteTimes)
    schedHtml = render_to_response("xgds_status_board/schedule.html", 
                                   {'eventList': eventList,
                                    'eventsPlusSiteTimes': eventsPlusSiteTimes,
                                    'STATUS_BOARD_TIMEZONES': settings.STATUS_BOARD_TIMEZONES,
                                    'STATUS_BOARD_DATE_TIMEZONE': timezones[settings.STATUS_BOARD_DATE_TIMEZONE],
                                    },
                                   context_instance=RequestContext(request))
    resultDict = {'schedHtml': schedHtml.content, 'localTimes': localTimes, 
                  'dateCount': eventList.count()}
    resultJson = json.dumps(resultDict)
    resp = HttpResponse(resultJson, mimetype='application/json')

    return resp

def getServerDatetimeJSON(request):
    timestamp = datetime.utcnow()
    times = getMultiTimezones(timestamp)
    result = []
    for time in times:
        datedict = {'dayName':time.strftime("%a"), 
                    'monthName':time.strftime("%b"),
                    'month':time.month, 'day':time.day, 
                    'year':time.year, 'shortyear':timestamp.strftime("%y"),
                    'hour':time.strftime("%H"),
                    'hour12':time.strftime("%I"),
                    'ampm':time.strftime("%p"),
                    'min':time.strftime("%M"),'sec':time.strftime("%S"),
                    'zone':time.tzinfo._tzname}
        result.append(datedict)
    datejson = json.dumps(result)

    return HttpResponse(datejson, mimetype='application/json')
