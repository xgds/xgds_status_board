var xgds_status_board = xgds_status_board || {};


// builds the UI and polls server for updates for each subsystem group
$(function() {
	function Widget(groupName, container, initialData) {
		this.groupName = groupName;
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
		this.el.html(this.template(this.data));
	};

	xgds_status_board.SubsystemStatusWidget = Widget;
});
