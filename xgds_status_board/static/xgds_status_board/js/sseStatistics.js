$(function() {
	function Widget(container, url) {
		this.container = container;
		this.url = url;
		this.errors = {};
		this.initialize();
		return this;
	};
	
	Widget.prototype.buildDataObject = function() {
		return {};
	};
	
	Widget.prototype.initialize = function() {
		var rawTemplate = $('#template-sse-statistics').html();
		this.template = Handlebars.compile(rawTemplate);
		this.data = this.buildDataObject();
		this.el = $(this.template(this.data));
		this.container.append(this.el);
	}
	
	Widget.prototype.update = function() {
		sse.subscribe(
			"redis_stats", 
			function (e) {
				let data = JSON.parse(e.data);
				data.message.data = JSON.parse(data.message.data);
				console.log("[SSE] [Redis Statistics]", data);
			}.bind(this),
			["redis_stats_sse"],
		);
	};

	Widget.prototype.render = function() {
		this.container.html(
			$(this.template(this.buildDataObject()))
		);
	};

	xgds_status_board.SseStatisticsWidget = Widget;
});
