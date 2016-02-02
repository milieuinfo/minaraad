/*! */
/*! Minaraad */

// Self wrapping closure
// Set strict on our scope.
(function(){
  "use strict";

  // Is everybody ready?
  $(function() {
    $(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt){
      setTimeout(function(){
        $('.masonry').masonry();
      }, 200);
    });
  });

})(); // end scope.
