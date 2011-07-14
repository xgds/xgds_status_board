# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import datetime
import logging

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404, HttpResponse

from geocamUtil import anyjson as json

from xgds_status_board.models import StatusboardAnnouncement, StatusboardEvent
from xgds_status_board import settings

def statusBoard(request):
    return render_to_response("xgds_status_board/gdsStatusBoard.html",
                              {'remoteTimezone': settings.REMOTE_TIMEZONE,
                              'localTimezone': settings.LOCAL_TIMEZONE,
                              'remoteTimezoneOffset': settings.REMOTE_TIMEZONE_OFFSET},
                              context_instance=RequestContext(request))

def statusBoardEdit(request):
    announcementList = StatusboardAnnouncement.objects.\
        order_by('-priority')
    return render_to_response("xgds_status_board/EditAnnouncements.html", 
                              {'announcements': announcementList},
                              context_instance=RequestContext(request))
    
def statusBoardAnnouncements(request):
    announcementList = StatusboardAnnouncement.objects.\
        filter(visible=True).order_by('-priority')
    return render_to_response("xgds_status_board/announcements.html", 
                              {'announcements': announcementList},
                              context_instance=RequestContext(request))

def addAnnouncement(request):
    if request.is_ajax():
        vis = bool(int(request.REQUEST['visible']))
        priority = request.REQUEST['priority']
        content = request.REQUEST['content']

        try:
            ann = StatusboardAnnouncement(priority=priority, visible=vis,content=content)
            ann.save()
            return HttpResponse(str(ann.id))
        except Exception:
            #logging.error(str(e))
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
        filter(visible=True).order_by('-priority')
    jsonList = []

    for announcement in announcementList:
        jsonList.append({'id': announcement.id, 
                         'priority': announcement.priority, 
                         'visible': announcement.visible,
                         'dateCreated':announcement.dateCreated.isoformat()+'Z',
                         'content': announcement.content})
       
    stuff = json.dumps(jsonList)
    return HttpResponse(stuff, mimetype='text/plain')

def statusBoardSchedule(request):
    eventList = StatusboardEvent.objects.\
        filter(visible=True).filter(completed=False).order_by('dateOfEvent')
    siteTimeOffset = datetime.timedelta(hours = settings.REMOTE_TIMEZONE_OFFSET)
    localTimes = [e.dateOfEvent.strftime("%m/%d/%Y %H:%M:%S") 
                  for e in eventList]
    siteTimes = [e.dateOfEvent + siteTimeOffset for e in eventList]
    eventsPlusSiteTimes = zip(eventList, siteTimes)
    schedHtml = render_to_response("xgds_status_board/schedule.html", 
                                   {'eventList': eventList,
                                    'eventsPlusSiteTimes': eventsPlusSiteTimes,
                                    'remoteTimezone': settings.REMOTE_TIMEZONE,
                                    'localTimezone': settings.LOCAL_TIMEZONE,
                                    'remoteTimezoneOffset': settings.REMOTE_TIMEZONE_OFFSET},
                                   context_instance=RequestContext(request))
    resultDict = {'schedHtml': schedHtml.content, 'localTimes': localTimes, 
                  'dateCount': eventList.count()}
    resultJson = json.dumps(resultDict)
    resp = HttpResponse(resultJson, mimetype='application/json')

    return resp

def getServerDatetimeJSON(request):
    timestamp = datetime.datetime.now()
    datedict = {'dayName':timestamp.strftime("%a"), 
                'monthName':timestamp.strftime("%b"),
                'month':timestamp.month, 'day':timestamp.day, 
                'year':timestamp.year, 'shortyear':timestamp.strftime("%y"),
                'hour':timestamp.strftime("%H"),
                'hour12':timestamp.strftime("%I"),
                'ampm':timestamp.strftime("%p"),
                'min':timestamp.strftime("%M"),'sec':timestamp.strftime("%S")}
    datejson = json.dumps(datedict)

    return HttpResponse(datejson, mimetype='application/json')
