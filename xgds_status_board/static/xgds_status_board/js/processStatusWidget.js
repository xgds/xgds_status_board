$(function() {
	function Widget(container, url) {
		this.url = url;
		this.container = container;
		this.initialize();
		return this;
	};

	Widget.prototype.buildHtml = function(listOfStatuses) {
		let string = "";
		for (let i of listOfStatuses)
		{
			string += `
				<tr>
					<td class="left subsystemName">{{displayName}}</td>
					<td
					class="status elapsedTime"
					style="background-color: {{color}}">
					{{status}}
					</td>
				</tr>
			`.replace('{{displayName}}', i.name).replace('{{color}}', i.color).replace('{{status}}', i.status);
		}
		return new Handlebars.SafeString(string);
	}

	Widget.prototype.buildDataObject = function() {
		let listOfStatuses = [];
		for (let key in this.statuses)
		{
			let status = this.statuses[key];
			let color = "#fc983a";
			if (status == "failed") color = "#ff0000";
			else if (status == "running") color = "#00ff00";
			listOfStatuses.push({
				'status': status,
				'color': color,
				'name': key,
			});
		}
		return {"table_contents": this.buildHtml(listOfStatuses)};
	};

	Widget.prototype.initialize = function() {
		this.template = Handlebars.compile($('#template-process').html());
		this.el = $(this.template(this.buildDataObject()));
		this.container.append(this.el);
	}

	Widget.prototype.update = function() {
		setInterval(function () {
			$.getJSON(this.url, function(statuses) {
				this.statuses = statuses;
				this.render();
			}.bind(this));
		}.bind(this), 5000);
		$.getJSON(this.url, function(statuses) {
			this.statuses = statuses;
			this.render();
		}.bind(this));
	};

	Widget.prototype.render = function() {
		this.el = $(this.template(this.buildDataObject()));
		this.container.html(this.el);
	};

	xgds_status_board.ProcessStatusWidget = Widget;
});
