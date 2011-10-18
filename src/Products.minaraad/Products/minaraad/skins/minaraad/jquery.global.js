/* Global jquery bindings for the site*/

(function($){
    function fix_attachment_forms() {
	// Fixes the problem with forms with attachments.
	// When submitting the form with the enter key, the first
	// submit is taken into account (instead of the global one).
	var forms = $('form');
	if (forms.length == 0) {
	    // No form on this page.
	    return;
	}
	
	forms.each(function() {
	    var form = $(this);
	    if (form.find('#attachment-controls').length == 0) {
		    // This form does not have a subform.
		    return;
	    }

	    form.find('input').keypress(function (e) {
		if (((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) && !$(this).parents().is('#attachment-controls')) {
		    // We only submit the main form if
		    // - user hit the 'enter' key
		    // - the field does not belong to the subform.
		    e.preventDefault();
		    form.trigger('submit');
		}
	    });
	});
    }

    $(document).ready(function(){
	fix_attachment_forms();
    });
})(jQuery)