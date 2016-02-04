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

        // Set listener on search buttons.
        $(".btn-search").click(function () {
          $(".search").slideToggle(
            "fast",
            function () {
              // TODO: only on slide open.
              $(".form-control").focus();
            });
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
      }, 200);

      // common_content_filter copied from Products/CMFPlone/skins/plone_ecmascript/popupforms.js
      var common_content_filter = '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info';

      // Activate the overlay on the newsletter link.
      $('#mailchimp_link a').prepOverlay(
        {
          subtype: 'ajax',
          filter: common_content_filter,
          // optional css class if needed:
          // cssclass: 'overlay-newsletter',
          //
          // Without matching formselector, the popup shows up fine.
          // But when you submit the loaded form, you end up on the
          // form page, instead of doing a submit inline.  Both have
          // valid use cases, but probably you want to stay on the
          // page.
          formselector: 'form#newsletter-subscriber-form',
          noform: function(el) {return $.plonepopups.noformerrorshow(el, 'close');}
        }
      );

  });

})(); // end scope.
