$(function() {
	function Widget(container, url, deleteUrl) {
		this.container = container;
		this.url = url;
		this.deleteUrl = deleteUrl;
		this.errors = {};
		this.initialize();
		return this;
	};

	Widget.prototype.buildTableOfErrors = function() {
		let string = "";
		for (let key in this.errors) // this.errors is an object (i.e. {})
		{
			let value = this.errors[key];
			string += ("<tr><td>" + 
			moment.unix(value.timestamp).utc().format(
				"YYYY/MM/DD HH:mm:ss") + 
				"</td><td>" +
				key +
				"</td><td>" + 
				value.error + 
				"</td><td>" + 
				'<button value="' + key + '">Clear</button>' +
				"</td></tr>"
			);
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
		)
		var deleteUrl = this.deleteUrl;
		this.container.find("button").click(
			function () {
				$.getJSON(
					deleteUrl + "?key=" + $(this).attr("value"),
					function (e) {},
				);
			}
		);
	};

	xgds_status_board.PersistentErrorsWidget = Widget;
});
