(function ($) {
    "use strict";

    /*	Table OF Contents
	==========================
	
	1.Navigation
	2.Sticky
	3.popup sign in & register 
	4.Parallax
	5.Parallax banner id div
	6.Theme change
	7.ScrollTop
	8.Subscribe Form
   
	
	/*===================
 
	
  /*===================
    1.Navigation
    ===================*/

    var leftPos, newWidth, isNavClicked = false,
        $mainNav_animate = $(".navbar-nav");

    $mainNav_animate.append("<li id='menu-icon'></li>");
    var $animation_tool = $("#menu-icon");

    $animation_tool
        .width($(".active").width())
        .css("left", $(".active").position().left)
        .data("origLeft", $(".active").position().left)
        .data("origWidth", $animation_tool.width());

    function xv_lava($el, speed) {
        leftPos = $el.position().left;
        newWidth = $el.width();
        $animation_tool.stop().animate({
            left: leftPos,
            width: newWidth,
        }, speed);
    }

    $(".navbar-nav a[href^='#']").click(function () {
        isNavClicked = true;
        $('.navbar-nav li').removeClass('active');
        $(this).parent().addClass('active');
        xv_lava($(this).parent(), 1000);
        $('html, body').animate({
            scrollTop: $($.attr(this, 'href')).offset().top - 65
        }, 1500, function () {
            isNavClicked = false;
        });
        return false;
    });
	
	
	
	 $(".pulse a[href^='#']").click(function () {
        isNavClicked = true;
        $('.pulse').removeClass('active');
        $(this).parent().addClass('active');
        xv_lava($(this).parent(), 1000);
        $('html, body').animate({
            scrollTop: $($.attr(this, 'href')).offset().top - 65
        }, 1500, function () {
            isNavClicked = false;
        });
        return false;
    });
	
	

    $(window).scroll(function () {
        if (!isNavClicked) {
            xv_lava($(".navbar-nav li.active"), 800);
        }
        if ($(window).scrollTop() >= 100) {


            if (!$("#main-nav").hasClass('slideInDown')) {
                $("#main-nav").addClass('animated slideInDown nav-shadow').removeClass('stickyNav');
            }
        } else if ($(window).scrollTop() <= 1) {
            if ($("#main-nav").hasClass('slideInDown')) {
                $("#main-nav").removeClass('animated slideInDown nav-shadow').addClass('stickyNav');
            }
        }

    });

    $('.navbar-nav li').hover(
        function () {
            if (!$(this).parents().hasClass('dropdown-menu')) {
                xv_lava($(this), 400);
            }
        }, function () {
            xv_lava($(".navbar-nav li.active"), 400);
        });


     
		

    /*===================
    2.Sticky
    ===================*/
    $(window).on("resize", function () {
        xv_lava($(".navbar-nav li.active"), 100);
		if( !$('#main-nav').hasClass('nav-stop')){
			$("#main-nav").sticky({topSpacing: 0});
		}
    }).resize();

  /*===================
   3.popup sign in & register 
    ===================*/	
	
	
	
	
	
	$("#login-menu").leanModal({top : 130, overlay : 0.6, closeButton: ".modal_close" });

	$(function(){
		// Calling Login Form
		$("#login_form").click(function(){
			$(".social_login").hide();
			$(".user_login").show();
			return false;
		});

		// Calling Register Form
		$("#register_form").click(function(){
			$(".social_login").hide();
			$(".user_register").show();
			$(".header_title").text('Signup');
			return false;
		});

		// Going back to Social Forms
		$(".back_btn").click(function(){
			$(".user_login").hide();
			$(".user_register").hide();
			$(".social_login").show();
			$(".header_title").text('Login');
			return false;
		});

	})
	
	
	

  
	
    /*===================
   4.Parallax
    ===================*/
  !function(n){var t=n(window),e=t.height();t.resize(function(){e=t.height()}),n.fn.parallax=function(o,i,r){function u(){var r=t.scrollTop();a.each(function(){var t=n(this),u=t.offset().top,c=h(t);r>u+c||u>r+e||a.css("backgroundPosition",o+" "+Math.round((l-r)*i)+"px")})}var h,l,a=n(this);a.each(function(){l=a.offset().top}),h=r?function(n){return n.outerHeight(!0)}:function(n){return n.height()},(arguments.length<1||null===o)&&(o="50%"),(arguments.length<2||null===i)&&(i=.1),(arguments.length<3||null===r)&&(r=!0),t.bind("scroll",u).resize(u),u()}}(jQuery);
  
   /*===================
  5.Parallax banner id div
    ===================*/
  
  (function($){
    "use strict";

    $(document).ready(function(){
      $('#lp-pom-block-10').parallax("50%", 0.3);
	   $('#lp-pom-block-11').parallax("50%", 0.3);
	   $('#lp-pom-block-12').parallax("50%", 0.3);
   
    }); 
  })(jQuery);
  
  
    
  
   /*===================
   6.Theme change
    ===================*/	 
	 
	 
$(document).ready(function() {
$(".styles-open").click(function(){
$(".styles, .styles-open").animate({ "left":"-230px" }, 1000); $(".styles-closed").animate({ "left":"0" }, 1000);
return false;
});
$(".styles-closed a").click(function(){
$(".styles-closed").animate({ "left":"-230px" },1000);
$(".styles").animate({ "left":"0" }, 1000);
$(".styles-open").animate({ "left":"115" }, 1000);
return false;
});
}); 
 
  
	/*===================
   7.ScrollTop
    ===================*/
	
	$(window).scroll(function(){
		 if ($(this).scrollTop() > 100) {
			 $('#go-top').fadeIn();
		 } else {
			 $('#go-top').fadeOut();
		 }
	 }); 
 
	 $('#go-top').click(function(e){
		 $("html, body").animate({ scrollTop: 0 }, 600);
		 e.preventDefault();
	 });
	 
	 

/*===================
   8.SUBSCRIBE FORM
    ===================*/	


$(document).ready(function() {
  $('#subscribeForm').ketchup().submit(function() {
      if ($(this).ketchup('isValid')) {
          var action = $(this).attr('action');
          $.ajax({
              url: action,
              type: 'POST',
              data: {
                  email: $('#address').val()
              },
              success: function(data){
                  $('#result').html(data);
              },
              error: function() {
                  $('#result').html('Sorry, an error occurred.');
              }
          });
      }
      return false;
  });
  
  

	
	
	
});

})(jQuery);