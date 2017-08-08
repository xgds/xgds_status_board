var xgds_status_board = xgds_status_board || {};

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
		result='<td class="status elapsedTime"><table class="loadAverage"><thead><th>1min</th><th>5min</th><th></th></thead>';
		result += '<tbody><tr id="' + sub["name"] +'_loadAverage"';
		result += '<td class="oneMin status">' + oneMin + '</td>';
		result += '<td class="fiveMin status">' + fiveMin + '</td></tr></tbody></table></td>';
	} else {
		result = '<td class="status elapsedTime" id="' + sub['name'] +'_status"';
		if ('statusColor' in sub && (!_.isEmpty(sub['statusColor']))) {
			result += 'style="background-color:' + sub['statusColor'] + '"';
		}
		result += '>' + sub['elapsedTime'] + '</td>';
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
