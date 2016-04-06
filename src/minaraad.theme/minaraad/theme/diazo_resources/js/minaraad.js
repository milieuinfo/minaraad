/*! */
/*! Minaraad */

// Self wrapping closure
// Set strict on our scope.
(function(){
    "use strict";

    // Is everybody ready?
    $(function() {

        /* Update masonry twice.  The first one after 200 milliseconds
         * may be too soon.  In that case the second one after a full
         * second should be fine.  If nothing needs to change between
         * these two calls, the user does not notice anything. */
        $(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt){
          setTimeout(function(){
            $('.masonry').masonry();
          }, 200);
        });
        $(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt){
          setTimeout(function(){
            $('.masonry').masonry();
          }, 1000);
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

      var common_content_filter = $.plonepopups.common_content_filter;

      // Activate the overlay on the newsletter footer link.
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

      // Activate the overlay on the newsletter detail link.
      $('#newsletter-mailchimp_link a').prepOverlay(
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

      // Activate the overlay on the login link.
      $('#login_link a').prepOverlay(
        {
          subtype: 'ajax',
          filter: common_content_filter,
          // formselector: 'form#login_form',
          noform: function(el) {return $.plonepopups.noformerrorshow(el, 'close');}
        }
      );

    });

  // Event attendees can be defined in a script tag on the MREvent pages.
  $(function($) {
    if (typeof event_attendees === 'undefined') {
      return;
    }
    var cookie = $.cookie('minaraad_attendee');
    if (!cookie) {
      return;
    }
    // Remove double quote at beginning and end.  Strange that they are there.
    if (cookie[0] === '"') {
      cookie = cookie.slice(1);
    }
    if (cookie[cookie.length - 1] === '"') {
      cookie = cookie.slice(0, cookie.length - 1);
    }
    var cookie_parts = cookie.split('#');
    if (cookie_parts.length !== 5) {
      return;
    }
    var hexdigest = cookie_parts[0];
    if (hexdigest.length !== 32) {
      // Not a proper hexdigest
      return;
    }
    var subscribed = false;
    for (var index = 0; index < event_attendees.length; index++) {
      if (event_attendees[index] === hexdigest) {
        subscribed = true;
        break;
      }
    }
    // By default, the subscribe button and form are shown.
    if (subscribed) {
      // Hide subscribe button and form, show unsubscribe button.
      $('#inschrijven').hide();
      $('#subscribe_button').hide();
      $('#unsubscribe_button').show();
    } else {
      // Fill in the values of the cookie, if nothing has been set yet.
      if (!$('#firstname').attr('value')) {
        $('#firstname').attr('value', cookie_parts[1]);
      }
      if (!$('#lastname').attr('value')) {
        $('#lastname').attr('value', cookie_parts[2]);
      }
      if (!$('#email').attr('value')) {
        $('#email').attr('value', cookie_parts[3]);
      }
      if (!$('#work').attr('value')) {
        $('#work').attr('value', cookie_parts[4]);
      }
    }

  });

  /* - toc.js - */
  /* Creates table of contents for pages for h[1234] */

  $(function($) {
      var dest, content, location, stack, oltoc, numdigits, wlh, target,
      targetOffset;

      dest = $('nav.toc section.nav-list div.nav-items');
      content = $('.container article:first');
      if (!content || !dest.length) {
          return;
      }

      dest.empty();

      location = window.location.href;
      if (window.location.hash) {
          location = location.substring(0, location.lastIndexOf(window.location.hash));
      }
      stack = [];
      // Get headers in document order
      $(content).find('*').not('.comment > h3').filter(function() {
          return (/^h[1234]$/).test(this.tagName.toLowerCase());
      })
      .not('.documentFirstHeading').each(function(i) {
          var level, ol, li;

          level = this.nodeName.charAt(1);
          // size the stack to the current level
          while (stack.length < level) {
              ol = $('<ul>');
              if (stack.length) {
                  li = $(stack[stack.length - 1]).children('li:last');
                  if (!li.length) {
                      // create a blank li for cases where, e.g., we have a subheading before any headings
                      li = $('<li>').appendTo($(stack[stack.length - 1]));
                  }
                  li.append(ol);
              }
              stack.push(ol);
          }
          while (stack.length > level) {
              stack.pop();
          }

          $(this).before($('<a name="section-' + i + '" />'));
          $('<li>').append(
          $('<a />').attr('href', location + '#section-' + i)
              .text($(this).text()))
              .appendTo($(stack[stack.length - 1]));
      });


      if (stack.length) {
          var oltoc = $(stack[0]);
          var i = 1;

          if (i <= stack.length) {
              $('nav.toc').show();
          }

          numdigits = oltoc.children().length.toString().length;
          //Use a clever class name to add margin that's MUCH easier to customize
          oltoc.addClass("TOC" + numdigits + "Digit");
          dest.append(oltoc);

          //scroll to element now.
          wlh = window.location.hash;
          if (wlh) {
              target = $(wlh);
              target = target.length && target || $('[name="' + wlh.slice(1) + '"]');
              targetOffset = target.offset();
              if (targetOffset) {
                  $('html,body').animate({
                      scrollTop: targetOffset.top
                  }, 0);
              }
          }
      }
  });

})(); // end scope.
