/*! */
/*! Minaraad */

// Self wrapping closure
// Set strict on our scope.
(function(){
    "use strict";

    // Is everybody ready?
    $(function() {

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

      // Build the wall
      // Add a tiny delay. Just enough to let grid items get their height.
      // This fixes the bottom margin.
      setTimeout(function() {
        $(".masonry").masonry({
          itemSelector: '.grid-item',
          columnWidth: '.grid-item',
          percentPosition: true
        });
      }, 1);

  });

})(); // end scope.
