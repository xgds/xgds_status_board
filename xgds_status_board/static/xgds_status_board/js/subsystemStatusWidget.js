var xgds_status_board = xgds_status_board || {};
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
		var subsystemNames = {ASD: "ASD", FTIR:"FTIR", video1:"video1"}; // list of subsystems to update status.
		function updateData() {
			$.getJSON(settings.XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL, subsystemNames, function(data) { self.render(data) });
		}
		setInterval(updateData, 1000);
	};

	Widget.prototype.render = function(data) {
		var rawTemplate = $('#template-subsystem-monitor').html();
		var compiledTemplate = Handlebars.compile(rawTemplate);
		var newDiv = compiledTemplate({'subsystemStatuses': data});
		this.domElement.html(newDiv);
	};

	// export
	xgds_status_board.SubsystemStatusWidget = Widget;
});
