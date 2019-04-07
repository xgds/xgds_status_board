$(function() {
	function Widget(container, url) {
		this.container = container;
		this.url = url;
		this.errors = {};
		this.initialize();
		return this;
	};

	Widget.prototype.buildTableOfErrors = function() {
		let string = "";
		for (let key in this.errors) // this.errors is an object (i.e. {})
		{
			let value = this.errors[key];
			string += "<tr><td>" + moment.unix(value.timestamp).utc().format("YYYY/MM/DD HH:mm:ss") + "</td><td>" + key + "</td><td>" + value.error + "</td></tr>";
		}
		return new Handlebars.SafeString(string);
	}
	
	Widget.prototype.buildDataObject = function() {
		return {
			'table_of_errors': this.buildTableOfErrors(),
		};
	};
	
	Widget.prototype.initialize = function() {
		var rawTemplate = $('#template-persistent-errors').html();
		this.template = Handlebars.compile(rawTemplate);
		this.data = this.buildDataObject();
		this.el = $(this.template(this.data));
		this.container.append(this.el);
	}
	
	Widget.prototype.update = function() {
		setInterval(function () {
			$.getJSON(
				this.url,
				function (errors) {
					this.errors = errors;
					this.render();
				}.bind(this),
			);
		}.bind(this), 1000);
	};

	Widget.prototype.render = function() {
		this.container.html(
			$(this.template(this.buildDataObject()))
		);
	};

	xgds_status_board.PersistentErrorsWidget = Widget;
});
