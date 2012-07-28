/* Table initialisation */

var tacdata;

var tables = {
	'hosts_table': {
		'aoColumnDefs': [
			{ 'sType': 'py-duration', 'aTargets': [ 4 ] },
			{ 'bSortable': false, 'sWidth': '12px', 'aTargets': [0] },
		]
	},
	'services_table': {
		'aoColumnDefs': [
			{ 'sType': 'py-duration', 'aTargets': [ 5 ] },
			{ 'bSortable': false, 'sWidth': '12px', 'aTargets': [0] }
		]
	}
};

var table_data = { 'hosts_table': { 'plugin_output': 5, 'id_col': 1, 'status': 2  },
	'services_table': { 'plugin_output': 7, 'id_col': 2, 'status': 3 } };
var table_filters = { 'UP': [ false, '#hosts_table' ], 'DOWN': [ true, '#hosts_table' ],
	'UNREACHABLE': [ true, '#hosts_table' ], 'OK': [ false, '#services_table '],
	'WARNING': [ true, '#services_table' ], 'CRITICAL': [ true, '#services_table' ],
	'UNKNOWN': [ true, '#services_table' ], 'hosts-pending': [ false, '#hosts_table' ],
	'services-pending': [ false, '#services_table' ] };
var unhandleds = { 'hosts': true, 'services': true };
var selected = { 'hosts_table': 0, 'services_table': 0 };
var timeout = null;

function get_statlabel(stattxt) {
	if(stattxt == 'UP')
		return '<span class="label label-success">' + stattxt + '</span>';
	else if(stattxt == 'DOWN')
		return '<span class="label label-important">' + stattxt + '</span>';
	else if(stattxt == 'UNREACHABLE')
		return '<span class="label label-inverse">' + stattxt + '</span>';
	else if(stattxt == 'OK')
		return '<span class="label label-success">' + stattxt + '</span>';
	else if(stattxt == 'WARNING')
		return '<span class="label label-warning">' + stattxt + '</span>';
	else if(stattxt == 'CRITICAL')
		return '<span class="label label-important">' + stattxt + '</span>';
	else if(stattxt == 'UNKNOWN')
		return '<span class="label label-inverse">' + stattxt + '</span>';
	else if(stattxt == 'PENDING')
		return '<span class="label label-info">' + stattxt + '</span>';
}

function create_table(table_name) {
	var table_def = {
		"sPaginationType": "bootstrap",
		"oLanguage": {
			"sLengthMenu": "_MENU_ records"
		},
		"sDom": "R<'row-fluid'<'span8'l><'span4'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
		"bAutoWidth": false,
		"bDeferRender": true,
		"fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
			var tableid = $(this).attr('id');
			var tattrs = table_data[tableid];
			var position = $(tableid).dataTable().fnGetPosition(nRow);
			var poc = $('td:eq(' + tattrs['plugin_output'] + ')', nRow);
			var poctxt = $(poc).text();
			if(poctxt.length > 40) {
				$(poc).text(poctxt.slice(0, 40) + '...');
				$(poc).tooltip({'title': poctxt});
			}

			var statrow = $('td:eq(' + tattrs['status'] + ')', nRow);
			$(statrow).html(get_statlabel($(statrow).text()));

			var auxdata = tacdata[tableid]['auxData'][position];
			if(tableid == 'hosts_table')
				name = tacdata[tableid]['data'][position][1];
			else
				name = tacdata[tableid]['data'][position][2];
			name += '&nbsp;';
			if(auxdata['problem_has_been_acknowledged'] == true)
				name += "<i class='icon-ok-circle' title='Acknowleged'></i>";
			if(auxdata['is_flapping'] == true)
				name += "<i class='icon-refresh' title='Is Flapping'></i>";
			if(auxdata['checks_enabled'] == false)
				name += "<i class='icon-question-sign' title='Checks Disabled'></i>";
			if(auxdata['notifications_enabled'] == false)
				name += "<i class='icon-ban-circle' title='Notifications Disabled'></i>";
			if(tableid == 'hosts_table')
				$('td:eq(' + tattrs['id_col'] + ')', nRow).html(name);
			else
				$('td:eq(' + tattrs['id_col'] + ')', nRow).html(name);

			$('i', nRow).tooltip();
			$('input', nRow).change(function() {
				var tableid = $(this).parents('table').attr('id');
				var state = $(this).prop('checked');
				var oldval;
				if(state)
					oldval = selected[tableid]++;
				else
					oldval = --selected[tableid];
				if(tableid == 'hosts_table') {
					if(state && oldval == 0) {
						$('#hosts_toolbar').collapse('show');
					} else if(!state && oldval == 0)
						$('#hosts_toolbar').collapse('hide');
				} else {
					if(state && oldval == 0)
						$('#services_toolbar').collapse('show');
					else if(!state && oldval == 0)
						$('#services_toolbar').collapse('hide');
				}

				if(state && oldval == 0)
					clearTimeout(timeout);
				if(!state && oldval == 0)
					refresh_data();
			});
		}
	}
	jQuery.extend(table_def, tables[table_name])
	$("#" + table_name).dataTable(table_def);
}

$.fn.dataTableExt.afnFiltering.push(
    function( oSettings, aData, iDataIndex ) {
		if(aData.length < 7) {
			if(unhandleds['hosts'] && aData[1] != 'OK') {
				var auxData = tacdata['hosts_table']['auxData'][iDataIndex];
				if(auxData['problem_has_been_acknowledged'])
					return false;
				else if(!auxData['notifications_enabled'])
					return false;
				else if(!auxData['checks_enabled'])
					return false;
			}

			if(aData[1] == 'PENDING')
				return table_filters['hosts-pending'][0];
			else
				return table_filters[aData[2]][0];
		}
		else {
			if(unhandleds['services'] && aData[3] != 'OK') {
				var auxData = tacdata['services_table']['auxData'][iDataIndex];
				if(auxData['problem_has_been_acknowledged'])
					return false;
				else if(!auxData['notifications_enabled'])
					return false;
				else if(!auxData['checks_enabled'])
					return false;
			}
			if(aData[3] == 'PENDING')
				return table_filters['services-pending'][0];
			else {
				return table_filters[aData[3]][0];
			}
		}
    }
);

function refresh_data() {
	$.getJSON('/frontend/cgi/tac2.py', function(data) {
		tacdata = data;
		for(var tn in tables) {
			for(var i = 0; i < data[tn]['data'].length; i++) {
				data[tn]['data'][i].unshift('<input type="checkbox">');
			}
			$('#' + tn).dataTable().fnClearTable();
			$('#' + tn).dataTable().fnAddData(data[tn]['data']);
		}

		for(var bn in table_filters) {
			var text = bn;
			if(text == 'hosts-pending' || text == 'services-pending')
				text = 'PENDING';
			text += ' (' + data['totals'][bn] + ')';
			$('#' + bn).text(text);
		}

		$('#loading_modal').modal('hide');
		
		timeout = setTimeout(function() {refresh_data()}, 30000);
	});
}

$(document).ready(function() {
	$('#loading_modal').modal();
	for(var tn in tables) {
		create_table(tn);
	}
	for(var dn in table_filters) {
		$('#' + dn).click(function() {
			var id = $(this).attr('id');
			table_filters[id][0] = !table_filters[id][0];
			$(table_filters[id][1]).dataTable().fnDraw();
		});
	}

	$('#hosts-unhandled').click(function() {
		unhandleds['hosts'] = !unhandleds['hosts'];
		$('#hosts_table').dataTable().fnDraw();
	});
	$('#services-unhandled').click(function() {
		unhandleds['services'] = !unhandleds['services'];
		$('#services_table').dataTable().fnDraw();
	});

	$.getJSON('/frontend/cgi/typeahead.py', function(data) {
		$('.search-query').typeahead({'source': data});
	});

	$('.collapse').collapse({ 'toggle': false });

	refresh_data();
} );
