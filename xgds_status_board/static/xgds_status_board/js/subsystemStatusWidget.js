var xgds_status_board = xgds_status_board || {};
$container = $('#container');


// renders the handlebars widget
function constructSubsystemMonitorView(subsystemStatusJson) {
	var rawTemplate = $('#template-subsystem-monitor').html();
	var compiledTemplate = Handlebars.compile(rawTemplate);
	var newDiv = compiledTemplate(subsystemStatusJson);
	var subsystemMonitorTemplate = $(newDiv);
	$container.append(subsystemMonitorTemplate);
}


// polls server for updates
$(function() {
	function Widget(domElement) {
		this.domElement = domElement;
		return this;
	}
	
	Widget.prototype.update = function() {
		var self = this;
		function updateData() {
			$.getJSON(settings.XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL, function(data) { self.render(data) });
		}
		setInterval(updateData, 1000);
	};

	Widget.prototype.render = function(data) {
		// update the colors based on data.
		console.log("data is ", data);
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
