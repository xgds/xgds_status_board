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
		function updateData() {
			$.getJSON(settings.XGDS_STATUS_BOARD_SUBSYSTEM_STATUS_URL, function(data) { self.render(data) });
		}
		setInterval(updateData, 1000);
	};

	Widget.prototype.render = function(statuses) {
		var buf = [];
		buf.push('<table class="recordingStatus">\n');
		buf.push('  <tr>\n');
		buf.push('    <th class="left">Name</th>\n')
		buf.push('    <th class="left">State</th>\n')
		buf.push('    <th>Last Updated</th>\n')
		buf.push('  </tr>\n');
		$.each(statuses, function(i, domainInfo) {
			buf.push('  <tr>\n');
			buf.push('    <td class="left">' + domainInfo.domain + '</td>\n');
			buf.push('    <td class="left">' + domainInfo.state + '</td>\n');
			buf.push('    <td class="left">' + domainInfo.timestamp + '</td>\n');
			buf.push('  </tr>\n');
		});
		buf.push('</table>\n');
		this.domElement.html(buf.join(''));
		
	};

	// export
	xgds_status_board.SubsystemStatusWidget = Widget;
});
