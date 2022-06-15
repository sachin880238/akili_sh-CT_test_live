odoo.define('website_sale_detail.website_sale_detail', function (require) {
    "use strict";
    
var ajax = require('web.ajax');


$( document ).ready(function() {

     // upload d0cument
	
    $('#ticket_attach_file').click(function(){
		$("#upload_attachment").val('no');
		$("#ticket_doc").val('');
		$('#oe_upload_document').modal('show');
    });


	$('#upload_attachment_submit').click(function(){
		$("#upload_attachment").val('yes');
    });

	$('.payment_select').click(function(){
		 var card = $('input[name=radio]:checked').val();
		 if (card == "credit_card"){
			$('input[name="radio_card"]').attr('checked', false);
			$("div.card_detail").removeClass("d-none");
			$("div.add_change_card").removeClass("d-none");
			$("div.credit_card_electrical").addClass("d-none");	
		 }
		 else if(card == "pay_electrical"){
		 	$('input[name="radio_card"]').attr('checked', false);
			$("div.card_detail").addClass("d-none");
			$("div.add_change_card").addClass("d-none");
			$("div.credit_card_electrical").removeClass("d-none");
		}
		else if(card == "manual"){
			$('input[name="radio_card"]').prop('checked', false);
			$("div.card_detail").addClass("d-none");
			$("div.add_change_card").addClass("d-none");
			$("div.credit_card_electrical").addClass("d-none");
		}
		
    });


	$('#add_change_card_click').click(function(){
		var payment_select = $('input[name=radio_card]:checked');
		$("#partner_id_model").val(document.getElementById('partner_id').value);
		$("#sale_order_id_model").val(document.getElementById('sale_order_id').value);
		$("#credit_card_detail_id").val(payment_select);
		if(payment_select.attr('id') != undefined){
			$("#credit_card_detail_id").val(payment_select.attr('id'));
			$("#debit_card_no").val(payment_select.attr('debit_card_no'));
			$("#card_holder_name").val(payment_select.attr('card_holder_name'));
			$("#month").val(payment_select.attr('month'));
			$("#year").val(payment_select.attr('year'));
			$("#change_card").removeClass("d-none");
			$("#add_card").addClass("d-none");
			$("#remove_card").removeClass("d-none");
		}
		else{
			$("#credit_card_detail_id").val('');
			$("#debit_card_no").val('');
			$("#card_holder_name").val('');
			$("#month").val('');
			$("#year").val('');
			$("#change_card").addClass("d-none");
			$("#add_card").removeClass("d-none");
			$("#remove_card").addClass("d-none");
		}

		$('#oe_credit_add_change').modal('show');
    });

	$('.submit_add_change_card').click(function(){
		var submit_value = $(this).val(); 
     	$("#card_value_add_or_change").val(submit_value);     
    });

	// canvas signature platform

	var $sigdiv = $("#signature").jSignature({'UndoButton':true});

    $('#click_prev_sign').click(function(){
		  var data = 
		  $('#output').val(signature?JSON.stringify(data[1]):false);

		  $('#sign_prev').attr('src',"data:"+data);
		  $('#sign_prev').show();
	});


	$('.signature-submit').click(function(){
		var signature = $sigdiv.jSignature('getData', 'image');
		var token = document.getElementById('token_signature').value;
		var order_id = document.getElementById('order_id').value;
		var customer_name = document.getElementById('customer_name').value;
		ajax.jsonRpc("/portal/signature", 'call',{
			'order_id': order_id,
			'token': token,
			'customer_name':customer_name,
			'sign': signature?JSON.stringify(signature[1]):false
		}).then(function (data) {
			window.location.href = '/my/orders/'+data.order_id.toString();

		});
		return true;


	});

	$('.clear_signature').click(function() {
		$('#sign_prev').hide();
	  	$sigdiv.jSignature('reset')
	  	$('#output').val('');
	});


	// reject quotation 
	$('#reject_quotation').click(function(){
		var order_id = $(this).attr("order_id");
		$("#modal_order_id").val(order_id);
		$('#popup_reject_quotation').modal('show');

	});

	$('#modal_reject_quotation').click(function(){
		var order_id = document.getElementById('modal_order_id').value;
		var reason = document.getElementById('reson_reject_quotation').value; 
		ajax.jsonRpc("/quote/reject", 'call', {
                    'order_id': order_id,
                    'reason':reason
                }).then(function (data) {
                    $('#popup_reject_quotation').modal('hide');
                    window.location.href = '/my/orders/'+data.order_id.toString();
                });
        return true;
	});



    var actve_btn = $('.updated_product_price');
    $(actve_btn).click(function(){
    	console.log("EWREWRQEWREWRQE@@@@@@@")
        ajax.jsonRpc('/fetch/saved_cart/record', 'call', {
                // 'name':'Website Header Icon Call Config Setting',
                
                }).then(function (data) {
                	console.log("BBBBBBBBBBBBBB")
                    
                });
        
    });





    $('.custom_merge_cart').off('click').on('click', function (event) {
            if (!event.isDefaultPrevented() && !$(this).is(".disabled")) {
                event.preventDefault();
                var $btn = $(this);
                var $cart_li_a = $('#top_menu li#my_cart_pop_over a');
                var $form = $btn.closest('form');
                var pid = document.getElementsByClassName('td-product')
                var pid1 = pid[0].getElementsByClassName("product11")
                var pro_id = pid1[0].attributes[5].nodeValue
                console.log("##################",pid1)
                console.log("##################111111",pid1[0].attributes[5].nodeValue)
                console.log("##################22222",pid1[0].innerHTML)
            


                var qty11 = document.getElementsByClassName('td-qty1')
                var qty12 = qty11[0].getElementsByClassName("quantity11")
                var pro_qty = qty12[0].innerHTML
                console.log("ASASASASSA",qty12)
                console.log("ASASASASSA1111",qty12[0].innerHTML)
                console.log("ASASASASSA1112222",qty12[0])



                var div_multi_product = document.getElementsByClassName("saved_multi_product")
                console.log("=====@@@@@@@@@@",div_multi_product)
                console.log("=====@@@@@@@111",div_multi_product[0].getElementsByClassName('td-product'))
     
                var product_multi_id=[]
                var product_Multi_qty=[]
                for(var i=0;i<parseInt(div_multi_product.length);i++){
                	console.log("12531275721356725723457",i)
                	var pid = div_multi_product[i].getElementsByClassName('td-product')
                	// console.log("************",pid)
	                var pid1 = pid[0].getElementsByClassName("product11")
	                var pro_id = pid1[0].attributes[5].nodeValue
	                console.log("$$$$$$$$$$$$$$",pro_id)

	                var qty11 = div_multi_product[i].getElementsByClassName('td-qty1')
	                var qty12 = qty11[0].getElementsByClassName("quantity11")
	                var pro_qty = qty12[0].innerHTML
	                console.log("____+++++++++++++",pro_qty)
                    // product_multi_id.push(pro_id)
                    // product_Multi_qty.push(parseInt(pro_qty))

                    var loading = '<span class="fa fa-cog fa-spin v_loading"/>';
	                $btn.text('Adding');
	                $btn.prepend(loading);
	                ajax.jsonRpc("/shop/cart/update_json", 'call', {
	                    'product_id': parseInt(pro_id),
	                    'add_qty': parseInt(pro_qty),
	                
	                }).then(function (data) {
	                    $cart_li_a.find('.my_cart_quantity').text(data.cart_quantity);
	                    ajax.jsonRpc('/fetch/current_cart', 'call', {
	                		'name':'Website Header Icon Call Config Setting',
	                
		                    }).then(function (data) {
		                        var phone_popup=document.getElementById('phone-model')
		                        phone_popup.style.display="none"
		                        var email_popup=document.getElementById('email-model')
		                        email_popup.style.display="none"
		                        var modal = document.getElementById("phone-model");
		                        var cart_modal = document.getElementById("cart-model");
		                        cart_modal.innerHTML=data
		                        
		                          
			                    modal.style.display = "none";
			                    cart_modal.style.display = "block";
			                    $btn.text('Merge');
		                        $btn.find('.v_loading').remove();
		                    });
	                	});

                }

            }

        });


});
});
function country_change(x) {
                             $.ajax({
                           url: "/country/state",
                           method: "POST",
                           contentType: 'application/json',
                           
                                data: JSON.stringify({"params": {
                                        'country_id':x.value,
                                        
                                    }}),
            success: function( data)  {

            	
            	var state_select_field = document.getElementById("state_id")
            	for (i = state_select_field.length - 1; i >= 1; i--) {
					state_select_field.remove(i);
				}
            for (var i in data.result)
              {
             var option = document.createElement("option");
			  option.text = data.result[i];
			  option.value=i
			  state_select_field.add(option);

              }
             },
            });}

 $(document).ready(function(){ 
    var tdprice2 = document.getElementsByClassName('oe_currency_value');

    var tdprice = $('#activeCartModal').find('tr');
    for (i = 1; i < tdprice.length; i++) {
        rec = tdprice[i]
        // for (i = 0; i < rec.length; i++) {

        //     console.log(";::::::::::::::::::::::::::::::::",rec)
        // }
        // var customerId = rec.getElementsByClassName("new_price");
      console.log(";::::::::::::::::::::::::::::::::",rec)
    }
    console.log("---------------------00000000000000000000---------------------",tdprice)
});


