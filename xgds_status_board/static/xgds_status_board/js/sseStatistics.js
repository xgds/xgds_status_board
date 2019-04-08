$(function() {
	function Widget(container, url) {
		this.container = container;
		this.url = url;
		this.statistics = {};
		this.initialize();
		return this;
	};

	Widget.prototype.buildTable = function () {
		let string = "";
		for (let key in this.statistics) // this.statistics is an object (i.e. {})
		{
			let value = this.statistics[key];
			string += "<tr><td>" + key + "</td><td>" + moment.utc(value.last).format("YYYY/MM/DD HH:mm:ss") + "</td><td>" + value.count + "</td></tr>";
		}
		return new Handlebars.SafeString(string);
	};
	
	Widget.prototype.buildDataObject = function() {
		return {"table": this.buildTable()};
	};
	
	Widget.prototype.initialize = function() {
		var rawTemplate = $('#template-sse-statistics').html();
		this.template = Handlebars.compile(rawTemplate);
		this.data = this.buildDataObject();
		this.el = $(this.template(this.data));
		this.container.append(this.el);
		this.render();
	};
	
	Widget.prototype.update = function() {
		sse.subscribe(
			"redis_stats", 
			function (e) {
				this.statistics = JSON.parse(JSON.parse(e.data).message.data);
				this.render();
			}.bind(this),
			"redis_statistics",
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
