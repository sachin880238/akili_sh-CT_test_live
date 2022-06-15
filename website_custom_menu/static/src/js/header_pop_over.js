odoo.define('website_custom_menu.call_popover', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');


    $( document ).ready(function() {
        var call_link = $('#top_menu li#call_pop_over');
        $(call_link).click(function(){
            ajax.jsonRpc('/fetch/color/record', 'call', {
                    'name':'Website Header Icon Call Config Setting',
                    
                    }).then(function (data) {
                        var phone_popup=document.getElementById('phone-model')
                        phone_popup.style.display="none"
                        var email_popup=document.getElementById('email-model')
                        email_popup.style.display="none"
                        var modal = document.getElementById("phone-model");
                        var main_content=modal.getElementsByClassName("popover-content-phone");
                        main_content[0].innerHTML=data.html_data   
                        var main_content_color=modal.getElementsByClassName("popover-title");
                        main_content_color[0].innerHTML=data.header_data+"<a href='#' onclick='close_phone_popup()' class='close' data-dismiss='alert'>×</a>"
                        // main_content_color[0].style.background=data.header_color

                        var content_cross_color=modal.getElementsByClassName("close");
                        content_cross_color[0].style.color=data.cross_color
                          
                          
                          
                        modal.style.display = "block";

                    });
            
        });
        $('body').on('click', function (e) { 
            if(!$(event.target).closest('#top_menu li#call_pop_over').length &!$(event.target).closest('#phone-model').length && !$(event.target).is('#phone-model')) {
     var modal = document.getElementById("phone-model");
              
              
            modal.style.display = "none";
   }  
});
    })
    
        // var call_link_popover;
        // $(call_link).onclick({
        //     trigger: 'manual',
        //     animation: true,
        //     html: true,
        //     title: function () {
        //         return _t("Call Us <a href='#' class='close' data-dismiss='alert'>&times;</a>");
        //     },
        //     container: 'body',
        //     placement: 'bottom',
        //     template: '<div class="popover call-popover my_custom_call_popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
        // }).on("click mouseenter",function () {
        //     $('.popover').popover('hide');
        //     var self = this;
        //     clearTimeout(call_link_popover);
        //     call_link.not(self).popover('hide');
        //     call_link_popover = setTimeout(function(){
        //         if($(self).is(':hover') && !$(".call-popover:visible").length)
        //         {
        //             $.get("/get/popover", {'type': 'call-popover'})
        //                 .then(function (data) {
        //                     $(self).popover({
        //                         trigger: 'hover',
        //                         placement: 'right',//left
        //                         html: true,
        //                         content: data
        //                     }).popover('show');
        //                     $(self).data("bs.popover").config.content =  data;
        //                     $(self).popover("show");
        //                     $('.my_custom_call_popover').find('.popover-title').html(_t("Call Us <a href='#' class='close' data-dismiss='alert'>&times;</a>"))
        //                     $('.my_custom_call_popover').find('.popover-content').html(data)
        //                     $(".popover").css('position', "fixed");
        //                     $(".popover").on("mouseleave", function () {
        //                         $(self).trigger('mouseleave');
        //                     });
        //                 });
        //         }
        //     }, 100);
        // }).on("mouseleave", function () {
        //     var self = this;
        //     setTimeout(function () {
        //         if (!$(".popover:hover").length) {
        //             if(!$(self).is(':hover')) {
        //                $(self).popover('hide');
        //             }
        //         }
        //     }, 100000);
        // });
    });

    // $('#my_cart_pop_over').click(function(){
    //     console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        
        // if (($('#password').attr('type'))=='text'){
        //     $("#password").attr("type","password");
        //     this.innerText = 'Show'
        // } else {
        //     $("#password").attr("type","text");
        //     this.innerText = 'Hide'
        // }
    // });


// comment dont want pop of login
// odoo.define('website_custom_menu.login_popover', function (require) {
//     "use strict";

//     var base = require('web_editor.base');
//     var core = require('web.core');
//     var _t = core._t;

//     $( document ).ready(function() {
//         var login_link = $('ul li#login_pop_over');
//         var login_link_popover;

//         $(login_link).popover({
//             trigger: 'manual',
//             animation: true,
//             html: true,
//             title: function () {
//                 return _t("Sign in to your account <a href='#' class='close' data-dismiss='alert'>&times;</a>");
//             },
//             container: 'body',
//             placement: 'bottom',
//             template: '<div class="popover login-popover my_custom_login_popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
//         }).on("mouseenter",function () {
//             var self = this;
//             $('.popover').popover('hide');
//             clearTimeout(login_link_popover);
//             login_link.not(self).popover('hide');
//             login_link_popover = setTimeout(function(){
//                 if($(self).is(':hover') && !$(".login-popover:visible").length)
//                 {
//                     $.get("/get/popover", {'type': 'login-popover'})
//                         .then(function (data) {
//                             $(self).popover({
//                     trigger:'manual',
//                     placement: 'manual',
//                     html: true,
//                     content: function(){
//                         return data;
//                     }
//                 }).popover('show');
//                             // popover-content
//                             $(self).data("bs.popover").config.content =  data;
//                             $(self).popover("show");
//                             $('.my_custom_login_popover').find('.popover-title').html(_t("Sign in to your account <a href='#' class='close' data-dismiss='alert'>&times;</a>"))
//                             $('.my_custom_login_popover').find('.popover-content').html(data)
//                             $(".popover").css('position', "fixed");
//                             $(".popover").on("mouseleave", function () {
//                                 $(self).trigger('mouseleave');
//                             });
//                         });
//                 }
//             }, 100);
//         }).on("mouseleave", function () {
//             var self = this;
//             setTimeout(function () {
//                 if (!$(".popover:hover").length) {
//                     if(!$(self).is(':hover')) {
//                        $(self).popover('hide');
//                     }
//                 }
//             }, 1000);
//         });
//     })
    
// });

odoo.define('website_custom_menu.cart', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');

    // var cart = require('website_sale.cart');
    $( document ).ready(function() {
        var shopping_cart_link = $('#top_menu li#my_cart_pop_over a');
        var shopping_cart_link_counter;
        $(shopping_cart_link).click(function(){
        //     $.ajax({
        //         url: "/fetch/current_cart/",
        //         method: "GET",
        //         dataType: "json",
        //         data: { product_id: 'Website Header Icon Call Config Setting'

        //         }
        // }).done(function(){
        //         console.log("========================99999",done)
        //     });
        ajax.jsonRpc('/fetch/current_cart', 'call', {
                    'name':'Website Header Icon Call Config Setting',
                    
                    }).then(function (data) {
                        var phone_popup=document.getElementById('phone-model')
                        phone_popup.style.display="none"
                        var email_popup=document.getElementById('email-model')
                        email_popup.style.display="none"
                        var modal = document.getElementById("phone-model");
                        var cart_modal = document.getElementById("cart-model");
                        console.log("------------------",data)
                        cart_modal.innerHTML=data
                        
                        
                          
                          
                          
                          modal.style.display = "none";
                          cart_modal.style.display = "block";
                    });
            
                        
                    
            
        });
        $('body').on('click', function (e) { 
            if(!$(event.target).closest('#top_menu li#my_cart_pop_over a').length &!$(event.target).closest('#cart-model').length && !$(event.target).is('#cart-model')) {
     var modal = document.getElementById("cart-model");
            console.log("hhhhhhhhhhhhhhhhhhhhh",modal)
              
              
            modal.style.display = "none";
   }  
});
        // shopping_cart_link.popover({
        //     trigger: 'manual',
        //     animation: true,
        //     html: true,
        //     title: function () {
        //         return _t("Cart Summary <a href='#' class='close' data-dismiss='alert'>&times;</a>");
        //     },
        //     container: 'body',
        //     placement: 'bottom',
        //     template: '<div class="popover mycart-popover my_custom_cart_popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
        // }).on("mouseenter",function () {
        //     console.log('mouseenter')
        //     $('.popover').popover('hide');
        //     var self = this;
        //     clearTimeout(shopping_cart_link_counter);
        //     shopping_cart_link.not(self).popover('hide');
        //     shopping_cart_link_counter = setTimeout(function(){

        //         if($(self).is(':hover') && !$(".mycart-popover:visible").length)
        //         {
                    
        //             $.get("/shop/cart", {'type': 'popover'})
        //                 .then(function (data) {

        //                     $(self).popover({
        //                         trigger: 'hover',
        //                         placement: 'right',//left
        //                         html: true,
        //                         content: data
        //                     }).popover('show');
        //                     $(self).data("bs.popover").config.content =  data;
        //                     $('.my_custom_cart_popover').find('.popover-title').html(_t("Cart Summary <a href='#' class='close' data-dismiss='alert'>&times;</a>"))
        //                     $('.my_custom_cart_popover').find('.popover-content').html(data)
        //                     $(self).popover("show");
        //                     $(".popover").css('position', "fixed");
        //                     $(".popover").on("mouseleave", function () {
        //                         $(self).trigger('mouseleave');
        //                     });

        //                     // $(self).data("bs.popover").config.content =  data;
        //                     // $(self).popover("show");
        //                     // $(".popover").css('position', "fixed");
        //                     // $(".popover").on("mouseleave", function () {
        //                     //     $(self).trigger('mouseleave');
        //                     // });
        //                 });
        //         }
        //     }, 100);
        // }).on("mouseleave", function () {
        //     var self = this;
        //     setTimeout(function () {
        //         if (!$(".popover:hover").length) {
        //             if(!$(self).is(':hover')) {
        //                $(self).popover('hide');
        //             }
        //         }
        //     }, 100);
        // })
    })

});

odoo.define('website_custom_menu.email_popover', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');

    $( document ).ready(function() {
        
        var email_link = $('#top_menu li#email_pop_over');
        
        $(email_link).click(function(){
            ajax.jsonRpc('/fetch/color/record', 'call', {
                    'name':'Website Header Icon Email Config Setting',
                    
                    }).then(function (data) {
                        var phone_popup=document.getElementById('phone-model')
                        phone_popup.style.display="none"
                        var email_popup=document.getElementById('email-model')
                        email_popup.style.display="none"
                        var modal = document.getElementById("email-model");
                        var main_content=modal.getElementsByClassName("email_popover_content");
                        main_content[0].innerHTML=data.html_data   
                        var main_content_color=modal.getElementsByClassName("mail-popover-title");
                        main_content_color[0].innerHTML=data.header_data+"<a href='#' onclick='close_email_popup()' class='close close-email' data-dismiss='alert'>×</a>"
                        main_content_color[0].style.background=data.header_color

                        var mail_cross_color=modal.getElementsByClassName("close");
                        mail_cross_color[0].style.color=data.cross_color
                           
                        modal.style.display = "block";
                        
                        
                });
            
        })
        $('body').on('click', function (e) { 
            if(!$(event.target).closest('#top_menu li#email_pop_over').length &!$(event.target).closest('#email-model').length && !$(event.target).is('#email-model')) {
            var modal = document.getElementById("email-model");
            console.log("hhhhhhhhhhhhhhhhhhhhh",modal)
              
              
            modal.style.display = "none";
   }  
});
    //     var email_modal = $('#top_menu li#email_pop_over');
    //     var email_link_popover;
    //     email_modal.popover({
    //         trigger: 'manual',
    //         animation: true,
    //         html: true,
    //         title: function () {
    //             return _t("Email Us <a href='#' class='close' data-dismiss='alert'>&times;</a>");
    //         },
    //         container: 'body',
    //         placement: 'bottom',
    //         template: '<div class="popover email-popover my_custom_email_popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
    //     }).on("click mouseenter",function (event) {
    //         var self = this;
    //         $('.popover').popover('hide');
    //         clearTimeout(email_link_popover);
    //         email_modal.not(self).popover('hide');
    //         email_link_popover = setTimeout(function(){
    //             if($(self).is(':hover') && !$(".email-popover:visible").length)
    //             {
    //                 $.get("/get/popover", {'type': 'email-popover'})
    //                     .then(function (data) {
    //                         $(self).popover({
    //                             trigger: 'hover',
    //                             placement: 'right',//left
    //                             html: true,
    //                             content: data
    //                         }).popover('show');
    //                         $(self).data("bs.popover").config.content =  data;
    //                         $('.my_custom_email_popover').find('.popover-title').html(_t("Email Us <a href='#' class='close' data-dismiss='alert'>&times;</a>"))
    //                         $('.my_custom_email_popover').find('.popover-content').html(data)
    //                         $(self).popover("show");
    //                         $(".popover").css('position', "fixed");
    //                         $(".popover").on("mouseleave", function () {
    //                             $(self).trigger('mouseleave');
    //                         });
    //                     });
    //             }
    //         }, 100);
    //     }).on("mouseleave", function () {
    //         var self = this;
    //         setTimeout(function () {
    //             if (!$(".popover:hover").length) {
    //                 if(!$(self).is(':hover')) {
    //                    $(self).popover('hide');
    //                 }
    //             }
    //         }, 100000);
    //     });
       })

});

odoo.define('website_custom_menu.common_popover', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function(){

        $(document).on("click", ".popover .close" , function(){
            $(this).parents(".popover").popover('hide');
        });

        $('body').on('click', function (e) {
            $('.popover').each(function () {
                if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                    $(this).popover('hide');
                }
            });
        });

        



    });
});
$("body").click(function() {
   if ($(".modale").is(":visible")) {
       $(".modale").hide();
   }
});

function close_phone_popup(argument) {
    console.log("--------------------------")
    var phone_popup=document.getElementById('phone-model')
    phone_popup.style.display="none"
    // body...
}


function close_email_popup(argument) {
    console.log("--------------------------")
    var email_popup=document.getElementById('email-model')
    email_popup.style.display="none"
    // body...
}
function close_cart_popup(argument) {
    console.log("--------------------------")
    var email_popup=document.getElementById('cart-model')
    email_popup.style.display="none"
    // body...
}


odoo.define('website_custom_menu.header_bckgrnd_color', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');


    $( document ).ready(function() {
        console.log("0000000000000000")
        ajax.jsonRpc('/fetch/web-color/record', 'call', {
            'name':'Website Header Color Config Setting',
            }).then(function (data) {
                var bckgrnd_color=document.getElementsByClassName('main-header')
                bckgrnd_color[0].style.background=data.web_header_bckgrnd_color

                var call_bkgrnd_color=document.getElementsByClassName("popover-title");
                var mail_bkgrne_color=document.getElementsByClassName("mail-popover-title");
                call_bkgrnd_color[0].style.background=data.web_header_bckgrnd_color
                mail_bkgrne_color[0].style.background=data.web_header_bckgrnd_color

                
                var menu_sidebar_color =document.getElementsByClassName("main-sidebar");
                menu_sidebar_color[0].style.background=data.web_header_bckgrnd_color

                call_bkgrnd_color[0].style.color=data.web_header_content_color
                mail_bkgrne_color[0].style.color=data.web_header_content_color

                var web_bar_color=document.getElementById("menu_open_btn");
                var web_conservation_icon=document.getElementsByClassName("conservation_tech");
                var web_call_color=document.getElementsByClassName("fa-phone");
                var web_mail_color=document.getElementsByClassName("fa-envelope");
                var web_search_color=document.getElementsByClassName("fa-search");
                var web_account_color=document.getElementsByClassName("fa-user");
                // var web_cart_color=document.getElementsByClassName("fa-shopping-cart");
                var web_cross_icon_color=document.getElementsByClassName("icon-times");
                var web_cross_color=document.getElementsByClassName("close");
                
                var my_cart_pop_over_color =document.getElementById("my_cart_pop_over");
                my_cart_pop_over_color.style.color=data.web_header_content_color
                web_bar_color.style.color=data.web_header_content_color
                web_conservation_icon[0].style.color=data.web_header_content_color
                web_call_color[0].style.color=data.web_header_content_color
                web_mail_color[0].style.color=data.web_header_content_color
                web_search_color[0].style.color=data.web_header_content_color
                web_account_color[0].style.color=data.web_header_content_color
                // web_cart_color[1].style.color=data.web_header_content_color
                web_cross_icon_color[0].style.color=data.web_header_content_color
                

                // var main_arrow_color = document.getElementsByClassName('arrow call');
                // console.log("000000001111111122222223333333",main_arrow_color)
                // main_arrow_color[0].setAttribute("data-after", 'web_bc_color');
                

                // var bk_color = window.getComputedStyle(
                //     document.querySelector('.arrow'), '::after'
                // ).setProperty('border-bottom-color','black');
                



            });
    });

});    




