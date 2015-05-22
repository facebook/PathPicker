$(window).resize(function() {
  console.log('resize called');
  if ($(window).width() < 768) {
    $("nav").addClass("navbar-fixed-top");
  } else {
    $("nav").removeClass("navbar-fixed-top");
  }
});

resize();