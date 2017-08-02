var xgds_status_board = xgds_status_board || {};
var $container = $('#container');

// renders the handlebars widget
function constructSubsystemMonitorView(subsystemStatusJson) {
	var rawTemplate = $('#template-subsystem-group').html();
	var compiledTemplate = Handlebars.compile(rawTemplate);
	var newDiv = $(compiledTemplate(subsystemStatusJson));
	$container.append(newDiv);
	return newDiv;
}


// polls server for updates
$(function() {
	function Widget(groupName, domElement) {
		this.el = el;
		this.groupName = groupName;
		return this;
	}
	
	Widget.prototype.update = function() {
		var context = this;
		function updateData() {
			var url = settings.XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL + '/' + groupName;
			$.getJSON(url, function(data) { context.render(data) });
		}
		setInterval(updateData, 1000); // update every second
	};

	Widget.prototype.render = function(data) {
		// update the colors based on data.
		$.each(data, function(group, subsystems) {
			data2 = data;
			$.each(subsystems, function(index, sub) {
				// set the status colors
				var statusId = group + "_" + sub['name'] + "_status";
				$('#' + statusId).css('background', sub['statusColor']);
				$('#' + statusId).html(sub['elapsedTime']);
				if (sub['name'].includes('LoadAverage')) {
					$('#' + sub['name']).find('td.oneMin').html(sub['oneMin']);
					$('#' + sub['name']).find('td.fiveMin').html(sub['fiveMin']);
				}
			});
		});
	};

	// export
	xgds_status_board.SubsystemStatusWidget = Widget;
});
