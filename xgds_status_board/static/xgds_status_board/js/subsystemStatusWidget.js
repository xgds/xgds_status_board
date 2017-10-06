var xgds_status_board = xgds_status_board || {};


var WARNING_TIME = 120;
var ERROR_TIME = 180;
var OKAY_COLOR = '#00ff00';
var	WARNING_COLOR = '#ffff00';
var	ERROR_COLOR = '#ff0000';
var OKAY = 0;
var WARNING = 1;
var ERROR = 2;
	

var calculateElapsedTime = function(lastUpdated, refreshRate){
	if (_.isUndefined(refreshRate) || _.isEmpty(refreshRate)){
		refreshRate = 60;
	}
	var result_color = ERROR_COLOR;
	var result_string = '';
	var duration = 2*refreshRate;
	var status = ERROR;
	try {
		if (!_.isUndefined(lastUpdated) && !_.isEmpty(lastUpdated)){
			var nowtime = moment.utc();
			var lasttime = moment.utc(lastUpdated);
			var delta = nowtime.diff(lasttime, 'seconds');
			duration = moment.duration(delta);
		    var result_string= sprintf('%02d:%02d:%02d', duration.hours(), duration.minutes(), duration.seconds());
		    if (delta * 1440 > 24){
		    		result_string = '> 1 day';
		    }
		
			if (delta >= 2*refreshRate && delta < 3*refreshRate){
				result_color = WARNING_COLOR;
				status = WARNING;
			} else if (delta < 2*refreshRate){
				result_color = OKAY_COLOR;
				status = OKAY;
			}
		}
	} catch (err) {
		// things are bad.
	}
	
	return {'color':result_color, 'time_string':result_string, 'delta': delta, 'status': status};
	
}

Handlebars.registerHelper('getDisplayValue', function(sub) {
	var result = '';
	if (!('name' in sub)){
		return '';
	}
	if (sub['name'].includes('LoadAverage')) {
		var oneMin = sub['oneMin'];
		if (oneMin === undefined){
			oneMin = '';
		}
		var fiveMin = sub['fiveMin']
		if (fiveMin === undefined){
			fiveMin = '';
		}
		result='<td class="status elapsedTime"><table class="loadAverage"><thead><th>1min</th><th>5min</th></thead>';
		result += '<tbody><tr id="' + sub["name"] +'_loadAverage">';
		result += '<td class="oneMin">' + oneMin + '</td>';
		result += '<td class="fiveMin">' + fiveMin + '</td></tr></tbody></table></td>';
	} else {
		var analyzedTime = calculateElapsedTime(sub['lastUpdated'], sub['refreshRate']);
		var color = analyzedTime.color;
		if ('statusColor' in sub && analyzedTime.status == OKAY ){
			color = sub['statusColor'];
		}
		result = '<td class="status elapsedTime" id="' + sub['name'] +'_status"';
		if (color !== undefined && color !== '') {
			result += 'style="background-color:' + color + '"';
		}

		result += '>' + analyzedTime.time_string + '</td>';

	}
	  return  new Handlebars.SafeString(result);
});

// builds the UI and polls server for updates for each subsystem group
$(function() {
	function Widget(groupName, container, initialData) {
		this.groupName = groupName;
		this.container = container;
		this.initialize(container, initialData)
		return this;
	};
	
	Widget.prototype.buildDataObject = function(newData) {
		return {'displayName': this.groupName,
			    'subsystem': newData}
	};
	
	Widget.prototype.initialize = function(container, initialData) {
		var rawTemplate = $('#template-subsystem-group').html();
		this.template = Handlebars.compile(rawTemplate);
		this.data = this.buildDataObject(initialData);
		this.el = $(this.template(this.data));
		container.append(this.el);
	}
	
	Widget.prototype.update = function() {
		var context = this;
		function updateData() {
			var url = settings.XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL  + context.groupName;
			$.getJSON(url, function(data) { context.render(data) });
		}
		setInterval(updateData, 1000); // update every second
	};

	Widget.prototype.render = function(data) {
		this.data = this.buildDataObject(data);
		this.el = $(this.template(this.data));
		this.container.html(this.el);
	};

	xgds_status_board.SubsystemStatusWidget = Widget;
});
