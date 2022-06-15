  odoo.define('website_custom_menu.website_custom_menu', function (require) {
    "use strict";
    /* Set the width of the side navigation to 250px */
     $(document).ready(function(){
        $('#menu_open_btn').click(function(){
           document.getElementById('menu_open_btn').style.display = "none";
           document.getElementById('menu_close_btn').style.display = "block";
           console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        });
        $('#menu_close_btn').click(function(){
           document.getElementById('menu_open_btn').style.display = "block";
           document.getElementById('menu_close_btn').style.display = "none";
           document.getElementsByClassName("main-sidebar").style.width = "0px !important;"
           // console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        });
      });




    $( document ).ready(function() {
        if (sessionStorage.menu_open == "true"){
            if ($('body').hasClass('sidebar-collapse')){
                // $('body').removeClass('sidebar-collapse');
            }
        }

        // START MENU OPEN ON CLICK OF TOGGLE
        if (!$('body').hasClass('sidebar-collapse')){
            $('#menu_open_btn').hide()
            $('#menu_close_btn').show();
            // sessionStorage.setItem('menu_open', false);
        } else {
            $('#menu_open_btn').show()
            $('#menu_close_btn').hide();
        }

        $('div.left_menu_toggle button').click(function(){
            if($(window).width() > 767){
                if ($('body').hasClass('sidebar-collapse') == false){
                    $('#menu_open_btn').show()
                    $('#menu_close_btn').hide();
                    sessionStorage.setItem('menu_open', false);
                } else {
                    $('#menu_open_btn').hide()
                    $('#menu_close_btn').show();
                    sessionStorage.setItem('menu_open', true);
                }
            }

            // JS ON OPEN AND CLOSE ON RESPONSIVE
            if($(window).width() <= 767){
                if ($('body').hasClass('sidebar-open') == true){
                    $('#menu_open_btn').show()
                    $('#menu_close_btn').hide();
                    sessionStorage.setItem('menu_open', false);
                } else {
                    $('#menu_open_btn').hide()
                    $('#menu_close_btn').show();
                    sessionStorage.setItem('menu_open', true);
                }
            }
        });
        // END MENU OPEN ON CLICK OF TOGGLE

        if($(window).width() <= 767){
            $('#menu_open_btn').show()
            $('#menu_close_btn').hide();
        }

        //START OPEN MENU WITH REFERENCE OF SESSION STORAGE
        // if($(window).width() > 767){
        //     if (sessionStorage.getItem('menu_open') == 'true'){
        //         $('#menu_open_btn').hide()
        //         $('#menu_close_btn').show();
        //         $('body').removeClass('sidebar-collapse');
        //     } 
        // }
        //END OPEN MENU WITH REFERENCE OF SESSION STORAGE

        // START JS FOR BACK TO TOP
        $('#back-to-top').click(function () {
            $('body,html').animate({
                scrollTop: 0
            }, 800);
            return false;
        });
        // END JS FOR BACK TO TOP
    });

});
