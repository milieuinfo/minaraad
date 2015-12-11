/*! */
/*! ${project} */

// Self wrapping closure
// Set strict on our scope.
(function(){
    "use strict";

    // Is everybody ready?
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

        // Toggle the drawer.
        var owner = $("#owner"),
          drawer = $("#drawer"),
          body = $("html body");
        // Click listeners
        $(owner).find("a.more").click(function () {
          $(owner).hide("fast");
          $(drawer).slideDown("slow");
          $("html, body").animate({scrollTop: $(document).height()}, "slow");
          return false;
        });
        $(drawer).find("a.less").click(function () {
          $(drawer).hide("fast");
          $(owner).slideDown("fast");
          return false;
        });
    });


})(); // end scope.
