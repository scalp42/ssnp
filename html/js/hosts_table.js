/* Table initialisation */
var dataurl = "/frontend/cgi/hosts_table.py";

function refresh_data() {
	$.getJSON(dataurl, function(data) {
		for(var i = 0; i < data['aaData'].length; i++) {
			var hstname = data['aaData'][i][0];
			hstname += "&nbsp;";
			var auxData = data['auxdata'][i];
			if(auxData['problem_has_been_acknowledged'] == true)
				hstname += "<i class='icon-ok-circle'></i>";
			if(auxData['is_flapping'] == true)
				hstname += "<i class='icon-refresh'></i>";
			if(auxData['checks_enabled'] == false)
				hstname += "<i class='icon-question-sign'></i>";
			if(auxData['notifications_enabled'] == false)
				hstname += "<i class='icon-ban-circle'></i>";
			data['aaData'][i][0] = hstname;

			statstr = data['aaData'][i][1];
			if(statstr == 'UP')
				statstr = '<span class="badge badge-success">' + statstr + '</span>';
			else if(statstr == 'DOWN' || statstr == 'UNREACHABLE')
				statstr = '<span class="badge badge-important">' + statstr + '</span>';
			else
				statstr = '<span class="badge">' + statstr + '</span>';
			data['aaData'][i][1] = statstr;
		}

		var htable = $('#hosts_table').dataTable();
		htable.fnClearTable();
		htable.fnAddData(data['aaData']);

		$('#hosts_table').popover('hide');
		setTimeout(function() { refresh_data() }, 30000);
	});
}

$(document).ready(function() {
	$('#hosts_table').popover({
		'animation': true,
		'trigger': 'manual',
		'title': 'Loading...',
		'content': 'Loading data from Nagios',
		'placement': 'bottom' });
	$('#hosts_table').popover('show');
	$('#hosts_table').dataTable( {
		"sPaginationType": "bootstrap",
		"oLanguage": {
			"sLengthMenu": "_MENU_ records per page"
		},
		"aoColumnDefs": [
			{ "sClass": "plugin_output", "aTargets": [4] },
			{ "sType": "py-duration", "aTargets": [3] }
		],
		"sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
		"bAutoWidth": false,
		"bDeferRender": true,
		"bStateSave": true,
		"fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
			$('td:eq(4)', nRow).tooltip({'title': aData[4]});
			$('.icon-ok-circle', nRow).tooltip({'title': 'Acknowledged'});
			$('.icon-refresh', nRow).tooltip({'title': 'Is Flapping'});
			$('.icon-question-sign', nRow).tooltip({'title': 'Checks Disabled'});
			$('.icon-ban-circle', nRow).tooltip({'title': 'Notifications Disabled'});
		}
	});

	var query = window.location.href.slice(window.location.href.indexOf('?') + 1);
	if(query)
		dataurl += '?' + query;

	refresh_data();
});
