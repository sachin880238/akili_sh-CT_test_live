odoo.define('website_drop_in_cart_block.website_sale', function (require) {
    "use strict";

    var base = require('web_editor.base'),
        ajax = require('web.ajax'),
        core = require('web.core'),
        utils = require('web.utils'),
        // Model = require('web.Model'),
        _t = core._t;

    // Document Ready   START
    $( document ).ready(function() {

        var $rows_branch = $('.search-branch');
        $('#search_product_by_name').keyup(function(e) {
            var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
            $rows_branch.show().filter(function() {
                var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
                var check = !~text.indexOf(val);
                var productDiv = $(this).parent().parent().parent().parent()
                if(check == false){
                    $(this).show()
                    $(this).prev().show()
                    $(this).parent().parent().parent().parent().show()
                    $(this).prev().parent().parent().parent().parent().show()
                }
                else{
                    $(this).hide()
                    $(this).prev().hide()
                    $(this).parent().parent().parent().parent().hide()
                    $(this).prev().parent().parent().parent().parent().hide()
                }
                return check    
            })
        });

        $('#parent_categ').on( "change", function() {
            $('input[name="search_product_by_name"]').val("");
            $('input[name="search_product_by_stock"]').val("");
            $('#find-a-product').submit();
        })

        $('#child_categ_1').on( "change", function() {
            $('input[name="search_product_by_name"]').val("");
            $('input[name="search_product_by_stock"]').val("");
            $('#find-a-product').submit();
        })

        $('#child_categ_2').on( "change", function() {
            $('input[name="search_product_by_name"]').val("");
            $('input[name="search_product_by_stock"]').val("");
            $('#find-a-product').submit();
        })


        $(".find-a-product-name").on( "click", function() {
            $('input[name="search_product_by_stock"]').val("");
        });

        $(".find-a-product-stock").on( "click", function() {
            $('input[name="search_product_by_name"]').val("");
        });

        $("input[name='search_product_by_name']").on( "keypress", function() {
            if (e.key == 'Enter'){
                $('input[name="search_product_by_stock"]').val("");
                e.preventDefault();
                $('#find-a-product').submit();
            }
        });
        $("input[name='search_product_by_stock']").on( "keypress", function() {
            if (e.key == 'Enter'){
                $('input[name="search_product_by_name"]').val("");
                e.preventDefault();
                $('#find-a-product').submit();
            }
        });
    })
    // Document Ready   END

});

function loadMore(){
    var length=0;
    var data= document.getElementById("search_detail").querySelectorAll(".oe_product_template_extension");
    for(var i=0;i<=data.length-1;i++){
        if(data[i].style.display=="" || data[i].style.display=="block"){
            length=length+1
        }
        
    }
    for(var j=length;j<=length+2;j++){
        if(data[j]==null){
            
        }
        else{
        data[j].style.display="block"}
    }
   $(window).bind('scroll');
   
}


function pagination_work(){
        var data= document.getElementById("search_detail").querySelectorAll(".oe_product_template_extension");
    for(var i=4;i<=data.length-1;i++){
        data[i].style.display="none"
    }
}


