function updateData() {
	$.getJSON(settings.XGDS_STATUS_BOARD_PROCESS_STATUS_URL, function(data) {
		window.processStatus = data;
	});
};
setInterval(updateData, 5000);