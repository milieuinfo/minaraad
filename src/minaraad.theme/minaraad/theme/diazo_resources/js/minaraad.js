/*! */
/*! ${project} */

// Self wrapping closure
// Set strict on our scope.
(function(){
    "use strict";

    // ${project} JS here...
    console.log("Hello Minaraad World!");

    $(function() {
        // Truncate paragraphs.
        var paragraphs = $("p.truncate");
        $.each(paragraphs, function (index, paragraph) {
          var height = 0,
            i = 1,
            words,
            text,
            previous_text,
            previous_previous_text;
          words = paragraph.textContent.split(/\s+/);
          if ($(paragraph).height() > 75) {
            while (height < 75) {
              previous_previous_text = previous_text;
              previous_text = text;
              text = paragraph.textContent = words.slice(0, i).join(' ');
              height = $(paragraph).height();
              i++;
            }
            paragraph.textContent = previous_previous_text + ' ...';
          }
        });
    });


})(); // end scope.