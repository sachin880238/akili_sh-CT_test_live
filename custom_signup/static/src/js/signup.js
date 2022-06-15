odoo.define('signup.signup', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;

    var ajax = require('web.ajax');

$( document ).ready(function() {

    $('#login_via_otp').click(function(){
        $('[name="login_via_otp"]').val("True");    
        $(this).closest('form').submit();
    })

    // Show password will show and make '*' in checkout signin password
 	$('.show-password').click(function(){
        if (($('#password_check').attr('type'))=='text'){
            $("#password_check").attr("type","password");
            this.innerText = 'show'
        } else {
            $("#password_check").attr("type","text");
            this.innerText = 'hide'
        }
    });


    // Validate email on test button
    $('.validateEmail').click(function(){
        console.log("QQQQQQWWEEEEERRRRRRRTTTTTTTYYYYYYYYY")
        var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
        var reg1 = document.getElementById('login');

        if (reg.test(reg1.value) == false) 
        {
            alert('Invalid Email Address');
            return false;
        }
    
        return true;
    });

    // This will generate otp and send otp on mobile number.
    $('.text-a-code').click(function(){
        var login = $('[name="login"]').val()
        
        ajax.jsonRpc("/text-a-new-code", 'call', {
            'login': login 
        }).done(function(data){
            if (data.otp_mobile_no){
                $('.text-a-code').popover({
                    content: _t("OTP sent on " + data.otp_mobile_no),
                    title: _t("Text sent."),
                    placement: "top",
                    trigger: 'focus',
                });
                $('.text-a-code').popover('show');
                setTimeout(function() {
                    $('.text-a-code').popover('destroy')
                }, 4000);
            }
        });
    });
    });

});


$(function () {
    $("#password_sign").click(function () {
        if ($(this).is(":checked")) {
            $(".password_individual").show();
        } else {
            $(".password_individual").hide();
        }
    });
});

$(function () {
    $("#security_question").click(function () {
        if ($(this).is(":checked")) {
            $("#security_questions_div").show();
        } else {
            $("#security_questions_div").hide();
        }
    });
});

$(function () {
    $("#email_sign").click(function () {
        if ($(this).is(":checked")) {
            $("#password_value").hide();
            $(".password_individual").hide();
        }
    });
});
