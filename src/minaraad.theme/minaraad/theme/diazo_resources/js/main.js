/*! */
/*! Minaraad */

// Self wrapping closure
// Set strict on our scope.
(function(){
    "use strict";

    // Is everybody ready?
    $(function() {
        $('.faceted-results').bind("DOMSubtreeModified", function() {
            if ($('.masonry').children().length == 0)
                return;
            setTimeout(function(){
                $('.masonry').masonry();
                console.log('called masonry')
            }, 1000);

        });
  });

})(); // end scope.
