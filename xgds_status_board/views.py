# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404

from geocamUtil import anyjson as json

from xgds_status_board.models import StatusboardAnnouncement, StatusboardEvent
from xgds_status_board import settings

def statusBoard(request):
    return render_to_response("xgds_status_board/gdsStatusBoard.html",
                              {'form': 'Funky Chicken'},
                              context_instance=RequestContext(request))

def statusBoardAnnouncements(request):
    announcementList = StatusboardAnnouncement.objects.\
        filter(visible=True).order_by('-priority')
    return render_to_response("xgds_status_board/announcements.html", 
                              {'announcements': announcementList},
                              context_instance=RequestContext(request))

def statusBoardSchedule(request):
    eventList = StatusboardEvent.objects.\
        filter(visible=True).filter(completed=False).order_by('dateOfEvent')
    siteTimeOffset = datetime.timedelta(hours = settings.HMP_TIME_OFFSET)
    localTimes = [e.dateOfEvent.strftime("%m/%d/%Y %H:%M:%S") 
                  for e in eventList]
    siteTimes = [e.dateOfEvent + siteTimeOffset for e in eventList]
    eventsPlusSiteTimes = zip(eventList, siteTimes)
    schedHtml = render_to_response("xgds_status_board/schedule.html", 
                                   {'eventList': eventList,
                                    'eventsPlusSiteTimes': eventsPlusSiteTimes},
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
