odoo.define('custom_init.custom_init', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;

    // Document Ready   START
    $( document ).ready(function() {
        var logout_timer = $('#logout_timer').val();
        var user_id = $('#user_id').val();
        var start_count_after_seconds = parseInt(logout_timer) - 30

        if ((user_id != '4') && logout_timer){
            window.onload = reset_main_timer;
            document.onmousemove = reset_main_timer;
            document.onkeypress = keyboard_action;
            var main_timer = 0;
            var countdown_timer = 0;

            function keyboard_action(){
                reset_main_timer();
                $("#logoutModal").modal("hide");
            }

            function countdown_timer_interval(minutes = 0, seconds = 30){
                clearInterval(countdown_timer);
                jQuery(".logout-count-down").html(minutes + ":" + seconds);
                countdown_timer = setInterval(function(){ 
                    console.log(minutes)
                    if(parseInt(minutes) == 0 && seconds == 0) { 
                        clearInterval(countdown_timer);
                        var base_url = window.location.origin;
                        window.location.href = base_url + "/web/session/logout?redirect=/" 
                    } else {
                        jQuery(".logout-count-down").html(minutes + ":" + seconds);
                         if(seconds == 0) { 
                            minutes--; 
                            if(minutes < 10) minutes = "0"+minutes;
                            seconds = 59;
                        } 
                        seconds--; 
                    } 
                }, 1000);
            }

            function dialog_set_interval(){
                main_timer = setInterval(function(){
                    $("#logoutModal").modal("show");
                    clearInterval(main_timer);
                    countdown_timer_interval();
                }, start_count_after_seconds * 1000);
            }

            function reset_main_timer(){
                clearInterval(main_timer);
                dialog_set_interval();
            }

            $('.continue_ok').click(function(){
                clearInterval(main_timer);
                dialog_set_interval();
            });

            $('.continue_ok').click(function(){
                clearInterval(main_timer);
                dialog_set_interval();
            });

            $('.logout_ok').click(function(){
                var base_url = window.location.origin;
                window.location.href = base_url + "/web/session/logout?redirect=/" 
            });
        }
    })
    // Document Ready   END

});
