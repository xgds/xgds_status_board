var xgds_status_board = xgds_status_board || {};

$container = $('#container');

// renders the handlebars widget
function constructSubsystemMonitorView() {
	var rawTemplate = $('#template-subsystem-monitor').html();
	var compiledTemplate = Handlebars.compile(rawTemplate);
	var newDiv = compiledTemplate({'ev1_icon': 'https://placekitten.com/200/200',
									'ev2_icon': 'https://placekitten.com/200/200'});
	var subsystemMonitorTemplate = $(newDiv);
	$container.append(subsystemMonitorTemplate);
}

// polls server for updates
$(function() {
	function getStatusTd(serviceInfo) {
		if (serviceInfo.status == 'running') {
			return '    <td class="center ok">' + serviceInfo.procStatus + '</td>\n';
		} else {
			return '    <td class="center error">' + serviceInfo.procStatus +  '</td>\n';
		}
	}

	function Widget(domElement) {
		this.domElement = domElement;
		return this;
	}

	Widget.prototype.update = function() {
		var self = this;
		var subsystemNames = {gpsController1: 'gpsController1', 
							  gpsController2: 'gpsController2', 
							  gpsDataQuality1: 'gpsDataQuality1', 
							  gpsDataQuality2: 'gpsDataQuality2', 
							  telemetryListener1: 'telemetryListener1', 
							  telemetryListener2: 'telemetryListener2', 
							  videoRecorder1: 'videoRecorder1', 
							  videoRecorder2: 'videoRecorder2', 
							  FTIR: 'FTIR', 
							  ASD: 'ASD', 
							  redCamera: 'redCamera',  
							  saCamera: 'saCamera', 
							  video1: 'video1', 
							  video2: 'video2', 
							  telemetryCleanup: 'telemetryCleanup', 
							  dataReplication1: 'dataReplication1', 
							  dataReplication2: 'dataReplication2'}; // list of subsystems to update status.
		
		function updateData() {
			$.getJSON(settings.XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL, subsystemNames, function(data) { self.render(data) });
		}
		setInterval(updateData, 1000);
	};

	Widget.prototype.render = function(data) {
		// get the data, update the matching id's status and color
		$.each(data, function( index, subsystem ) {
			// set status color
			$('#'+subsystem['name']).find('td.status').css('background', subsystem['statusColor']);
			// set last updated time 
			var updatedTime = $('#'+subsystem['name']).find('td.updatedTime');
			if (updatedTime.length) {
				updatedTime.html(subsystem['lastUpdated']);	
			}
		});
	};

	// export
	xgds_status_board.SubsystemStatusWidget = Widget;
});
