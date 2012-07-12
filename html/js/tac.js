/* Table initialisation */

var obj_types = [ 'hosts', 'services' ];
var states = { 'hosts': [ 'down', 'unreachable', 'pending', 'up' ],
	'services': [ 'warning', 'critical', 'unknown', 'pending', 'ok' ] };
var output_columns = { 'hosts': 3, 'services': 5 };
var duration_columns = { 'hosts': 2, 'services': 3 };
var sorting_defs = { 'hosts': [ [ 2, 'asc' ], [ 0, 'asc' ] ],
	'services': [ [ 3, 'asc' ], [ 0, 'asc' ], [ 1, 'asc' ] ] };

function create_table(o, s) {
	$("#" + obj_types[o] + "_" + states[obj_types[o]][s] + "_table").dataTable( {
		"sPaginationType": "bootstrap",
		"oLanguage": {
			"sLengthMenu": "_MENU_ records per page"
		},
		"sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
		"bAutoWidth": false,
		"bDeferRender": true,
		"aoColumnDefs": [
			{ "sClass": "plugin_output", "aTargets": [ output_columns[obj_types[o]] ] },
			{ "sType": "py-duration", "aTargets":[ duration_columns[obj_types[o]] ] }
		],
		"aaSorting": sorting_defs[obj_types[o]],
		"bStateSave": true,
		"fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
			$('td:eq(' + output_columns[obj_types[o]] + ')', nRow).tooltip(
				{'title': aData[output_columns[obj_types[o]]]});
		}
	});
}

function refresh_data() {
	$.getJSON('/frontend/cgi/tac.py', function(data) {
		for(var o = 0; o < obj_types.length; o++) {
			var ostr = obj_types[o];
			var otd = output_columns[obj_types[o]];
			for(var s = 0; s < states[obj_types[o]].length; s++) {
				var sstr = states[ostr][s];
				var selector = "#" + ostr + "_" + sstr + "_table";
				var table = $(selector).dataTable();
				$(selector).dataTable().fnClearTable();
				$(selector).dataTable().fnAddData(data[ostr][sstr]);
				var tablink = "#" + ostr + "_" + sstr + "_tablink";
				$(tablink).text(sstr.toUpperCase() + ' (' + 
					data[ostr][sstr].length + ')');
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
