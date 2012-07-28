/* Table initialisation */

var obj_types = [ 'hosts', 'services' ];
var states = { 'hosts': [ 'down', 'unreachable', 'pending', 'up' ],
	'services': [ 'warning', 'critical', 'unknown', 'pending', 'ok' ] };
var output_columns = { 'hosts': 3, 'services': 5 };
var duration_columns = { 'hosts': 2, 'services': 3 };
var sorting_defs = { 'hosts': [ [ 2, 'asc' ], [ 0, 'asc' ] ],
	'services': [ [ 3, 'asc' ], [ 0, 'asc' ], [ 1, 'asc' ] ] };
var tacdata;

function create_table(o, s) {
	var otype = obj_types[o];
	var table_def = {
		"sPaginationType": "bootstrap",
		"oLanguage": {
			"sLengthMenu": "_MENU_ records per page"
		},
		"sDom": "R<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
		"bAutoWidth": false,
		"bDeferRender": true,
		"aoColumnDefs": [
			{ "sClass": "plugin_output", "sWidth": "275px", "aTargets": [ output_columns[otype] ] },
			{ "sType": "py-duration", "aTargets":[ duration_columns[otype] ] }
		],
		"aaSorting": sorting_defs[otype],
		"bStateSave": true,
		"fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
			$('td:eq(' + output_columns[otype] + ')', nRow).tooltip(
				{'title': aData[output_columns[otype]]});
			$('.icon-ok-circle', nRow).tooltip({'title': 'Acknowledged'});
			$('.icon-refresh', nRow).tooltip({'title': 'Is Flapping'});
			$('.icon-question-sign', nRow).tooltip({'title': 'Checks Disabled'});
			$('.icon-ban-circle', nRow).tooltip({'title': 'Notifications Disabled'});
		}
	}

	if(otype == 'services')
		table_def['aoColumnDefs'].push({'sWidth': '70px', 'aTargets': [ 4 ] });

	$("#" + otype + "_" + states[otype][s] + "_table").dataTable(table_def);
}

function iconize(index, ostr, sstr) {
	var name;
	if(ostr == 'hosts')
		name = tacdata[ostr][sstr]['data'][index][0];
	else
		name = tacdata[ostr][sstr]['data'][index][1];
	var auxdata = tacdata[ostr][sstr]['auxData'][index];
	name += "&nbsp;";
	if(auxdata['problem_has_been_acknowledged'] == true)
		name += "<i class='icon-ok-circle'></i>";
	if(auxdata['is_flapping'] == true)
		name += "<i class='icon-refresh'></i>";
	if(auxdata['checks_enabled'] == false)
		name += "<i class='icon-question-sign'></i>";
	if(auxdata['notifications_enabled'] == false)
		name += "<i class='icon-ban-circle'></i>";
	return name;
}

function refresh_data() {
	$.getJSON('/frontend/cgi/tac.py', function(data) {
		tacdata = data;
		for(var o = 0; o < obj_types.length; o++) {
			var ostr = obj_types[o];
			var otd = output_columns[obj_types[o]];
			for(var s = 0; s < states[obj_types[o]].length; s++) {
				var sstr = states[ostr][s];
				for(var i = 0; i < data[ostr][sstr]['data'].length; i++) {
					if(ostr == 'hosts')
						data[ostr][sstr]['data'][i][0] = iconize(
							i, ostr, sstr);
					else
						data[ostr][sstr]['data'][i][1] = iconize(
							i, ostr, sstr);
				}
				var selector = "#" + ostr + "_" + sstr + "_table";
				var table = $(selector).dataTable();
				$(selector).dataTable().fnClearTable();
				$(selector).dataTable().fnAddData(data[ostr][sstr]['data']);
				var tablink = "#" + ostr + "_" + sstr + "_tablink";
				$(tablink).text(sstr.toUpperCase() + ' (' + 
					data[ostr][sstr]['data'].length + ')');
			}
		}

		$('#loading_modal').modal('hide');
		setTimeout(function() {refresh_data()}, 30000);
	});
}

$(document).ready(function() {
	$('#loading_modal').modal();
	for(var o = 0; o < obj_types.length; o++) {
		for(var s = 0; s < states[obj_types[o]].length; s++) {
			create_table(o, s);
		}
	}

	$.getJSON('/frontend/cgi/typeahead.py', function(data) {
		$('.search-query').typeahead({'source': data});
	});

	refresh_data();
} );
