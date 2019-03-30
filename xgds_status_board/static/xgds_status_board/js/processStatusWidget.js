$(function() {
	function Widget(groupName, container, initialData) {
		this.groupName = groupName;
		this.container = container;
		this.status = initialData;
		this.initialize(container, initialData)
		return this;
	};
	
	Widget.prototype.buildDataObject = function(newData) {
		if (this.status == "failed") this.color = "#ff0000";
		else if (this.status == "running") this.color = "#00ff00";
		else this.color = "#fc983a";
		return {
			'displayName': this.groupName,
			'status': this.status, 
			'color': this.color,
		};
	};
	
	Widget.prototype.initialize = function(container, initialData) {
		var rawTemplate = $('#template-process').html();
		this.template = Handlebars.compile(rawTemplate);
		this.data = this.buildDataObject(initialData);
		this.el = $(this.template(this.data));
		container.append(this.el);
	}
	
	Widget.prototype.update = function() {
		setInterval(function () {
			if (!window.processStatus) return;
			this.status = window.processStatus[this.groupName];
			this.render();
		}.bind(this), 1000);
	};

	Widget.prototype.render = function(data) {
		this.data = this.buildDataObject(data);
		this.el = $(this.template(this.data));
		this.container.html(this.el);
	};

	xgds_status_board.ProcessStatusWidget = Widget;
});
