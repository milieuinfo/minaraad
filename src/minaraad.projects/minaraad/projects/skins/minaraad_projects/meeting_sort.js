/* Allows quick sorting of the agenda items with some javascript */
jq(document).ready(function() {
    var table = jq('table#meeting_view');
    function row_dropped(t, r) {
	// We compute the position of the row.
	var position = 0;
	var found = false;
	table.find('tbody tr').each(function() {
	    if (found || this.id == r.id) {
		found = true;
		return;
	    }
	    position += 1;
	});

	jq.pyproxy_call('jq_meeting_order_changed',
			{'uid': r.id, 'position': position});
    }

    if (table.length == 0) {
	// There is no table on this page.
	return;
    }

    table.tableDnD({
	onDragClass: 'row_dragged',
	onDrop: row_dropped
    });
});