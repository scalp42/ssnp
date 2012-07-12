/* Table initialisation */
var dataurl = "/frontend/cgi/services_table.py";

function refresh_data() {
	$.getJSON(dataurl, function(data) {
		for(var i = 0; i < data['aaData'].length; i++) {
			var svcname = data['aaData'][i][1];
			svcname += "&nbsp;";
			var auxData = data['auxdata'][i];
			if(auxData['problem_has_been_acknowledged'] == true)
				svcname += "<i class='icon-ok-circle'></i>";
			if(auxData['is_flapping'] == true)
				svcname += "<i class='icon-refresh'></i>";
			if(auxData['checks_enabled'] == false)
				svcname += "<i class='icon-question-sign'></i>";
			if(auxData['notifications_enabled'] == false)
				svcname += "<i class='icon-ban-circle'></i>";
			data['aaData'][i][1] = svcname;

			statstr = data['aaData'][i][2];
			if(statstr == 'OK')
				statstr = '<span class="badge badge-success">' + statstr + '</span>';
			else if(statstr == 'WARNING')
				statstr = '<span class="badge badge-warning">' + statstr + '</span>';
			else if(statstr == 'CRITICAL')
				statstr = '<span class="badge badge-important">' + statstr + '</span>';
			else if(statstr == 'UNKNOWN')
				statstr = '<span class="badge badge-info">' + statstr + '</span>';
			else
				statstr = '<span class="badge">' + statstr + '</span>';
			data['aaData'][i][2] = statstr;
		}

		var stable = $('#services_table').dataTable();
		stable.fnClearTable();
		stable.fnAddData(data['aaData']);
		$('#services_table').popover('hide');
		setTimeout(function() { refresh_data() }, 30000);
	});
}

$(document).ready(function() {
	$('#services_table').popover({
		'animation': true,
		'trigger': 'manual',
		'title': 'Loading...',
		'content': 'Loading data from Nagios',
		'placement': 'bottom' });
	$('#services_table').popover('show');
	$('#services_table').dataTable( {
		"sPaginationType": "bootstrap",
		"oLanguage": {
			"sLengthMenu": "_MENU_ records per page"
		},
		"aoColumnDefs": [
			{ "sClass": "plugin_output", "aTargets": [6] },
			{ "sType": "py-duration", "aTargets": [4] }
		],
		"sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
		"bAutoWidth": false,
		"bDeferRender": true,
		"bStateSave": true,
		"fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
			$('td:eq(6)', nRow).tooltip({'title': aData[6]});
			$('.icon-ok-circle', nRow).tooltip({'title': 'Acknowledged'});
			$('.icon-refresh', nRow).tooltip({'title': 'Is Flapping'});
			$('.icon-question-sign', nRow).tooltip({'title': 'Checks Disabled'});
			$('.icon-ban-circle', nRow).tooltip({'title': 'Notifications Disabled'});
		}
	});

	var only_problems = $.getUrlVar('only_problems');
	if(only_problems)
		dataurl += '?only_problems=' + only_problems;

	refresh_data();
});
