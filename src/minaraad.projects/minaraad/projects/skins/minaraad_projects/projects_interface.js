jq(document).ready(function() {
    function hide_advisory_reasons() {
	if (!this.checked) {
	    return;
	}

        var disagreeing = jq('#archetypes-fieldname-disagreeing_members');
        var reasons = jq('#archetypes-fieldname-reject_reasons');

        if (this.value == 'abstention_rejection') {
            disagreeing.show();
            reasons.show();
        } else {
            disagreeing.hide();
            reasons.hide();
	}
    }

    hide_advisory_reasons();
    jq('input[name=advisory_type]').
	each(hide_advisory_reasons).
	change(hide_advisory_reasons).
	click(hide_advisory_reasons);

    // Handle submitting the link to other years in the
    // project/meeting overviews.
    var select_submit = jq('#select-year-submit');
    select_submit.hide();
    jq('select[name=year]').change(function () {
        select_submit.click();
    });


    jq('.attachment_publish_checkbox').click(function(e) {
	var data = {}
	data['att_uid'] = jq(this).attr('name').split('attachment_')[1];
	if (this.checked) {
	    data['published'] = true;
	}
	jq.pyproxy_call('jq_attachment_published_changed',
			data,
			function(){},
			this);
    });
});