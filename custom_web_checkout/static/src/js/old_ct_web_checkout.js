odoo.define('ct_web_checkout.ct_web_checkout', function (require) {
    "use strict";
    
var ajax = require('web.ajax');

$( document ).ready(function() {

    $('.show-password').click(function(){
        if (($('#password').attr('type'))=='text'){
            $("#password").attr("type","password");
        } else {
            $("#password").attr("type","text");
        }
    });

    $('.reset-password').click(function(){
        $("#password").val('')
    });

    // CHANGE RADIO BUTTON COMPANY AND INDIVIDUAL
    $('input[type=radio][name=company_type]').change(function() {
        if ($(this).val() == 'company'){
            $('#company_field').removeClass('hidden');
        } else {
            $('#company_field').addClass('hidden');
        }
    });

    $('#phone_number_test').click(function(){
        var phone = $('#telephone_number').val();
        ajax.jsonRpc("/check-number-is-valid", 'call', {
            'phone': phone
        }).then(function(data){
            if (data.valid == true){
                $('#messaget_not_valid').addClass("o_hidden");
                $('#messaget_valid').removeClass("o_hidden");   
            }
            else{
                $('#messaget_valid').addClass("o_hidden");
                $('#messaget_not_valid').removeClass("o_hidden");
            }
        })
            
    });


    $('.oe_cart').on('click', '.js_change_contacts', function() {
        if (!$('body.editor_enable').length) {
            var $old = $('.all_contact').find('.panel.border_primary');
            $old.find('.btn-contact').toggle();
            $old.find('.panel-footer').addClass('js_change_contacts');
            $old.removeClass('border_primary');

            var $new = $(this).parent('.panel-default').parent('div.one_kanban').find('.panel');
            $new.find('.btn-contact').toggle();
            $new.removeClass('js_change_contacts');
            $new.addClass('border_primary');

            var $form = $(this).parent('.panel-default').parent('div.one_kanban').find('form.hide');
            $.post($form.attr('action'), $form.serialize()+'&xhr=1');
          }
    });

    $('.oe_cart').on('click', '.js_change_billings', function() {
        if (!$('body.editor_enable').length) { //allow to edit button text with editor
            var $old = $('.all_billing').find('.panel.border_primary');
            $old.find('.btn-bill').toggle();
            $old.find('.panel-footer').addClass('js_change_billings');
            $old.removeClass('border_primary');

            var $new = $(this).parent('.panel-default').parent('div.one_kanban').find('.panel');
            $new.find('.btn-bill').toggle();
            $new.removeClass('js_change_billings');
            $new.addClass('border_primary');

            var $form = $(this).parent('.panel-default').parent('div.one_kanban').find('form.hide');
            $.post($form.attr('action'), $form.serialize()+'&xhr=1');
        }
    });


    $('.oe_cart').on('click', '.js_change_shippings', function() {
        if (!$('body.editor_enable').length) { //allow to edit button text with editor
            var $old = $('.all_shipping').find('.panel.border_primary');
            $old.find('.btn-ship').toggle();
            $old.find('.panel-footer').addClass('js_change_shippings');
            $old.removeClass('border_primary');

            var $new = $(this).parent('.panel-default').parent('div.one_kanban').find('.panel');
            $new.find('.btn-ship').toggle();
            $new.removeClass('js_change_shippings');
            $new.addClass('border_primary');

            var $form = $(this).parent('.panel-default').parent('div.one_kanban').find('form.hide');
            $.post($form.attr('action'), $form.serialize()+'&xhr=1');
        }
    });

	$('.js_delete_address').on('click', function(e) {
            var $elem = $(this),
                pid = parseInt($elem.attr('data-contact-id'));
            ajax.jsonRpc("/shop/partner/remove", 'call', {
                    'partner_id': pid,
                }).then(function (data) {
                    if (data && data.result){
                        $elem.closest('div.one_kanban').remove();
                    }
                    else if(data && data.error_message) {
                        $(`<div class="alert alert-danger">
                          `+ data.error_message.join('<br />') + `
                        </div>`).prependTo('div.oe_cart');
                    }
                });
    });


    // upload d0cument
	
    $('#order_attach_file').click(function(){
        $("#customer_priority_1").val(document.getElementById('customer_priority').value);
		$("#client_order_ref_1").val(document.getElementById('client_order_ref').value);
		$("#note_1").val(document.getElementById('note').value);
		$('#oe_upload_document').modal('show');
    });

	$(".modal").on("hidden.bs.modal", function(){
		$(".modal-body1").html("");
	});

    // START SAVE ORDER DETAIL ON ONCHANGE OF TEXT CONTENT
    $("form :input").change(function() {
        var customer_priority = $('#customer_priority').val();
        var client_order_ref = $('#client_order_ref').val();
        var note = $('#note').val();

        ajax.jsonRpc("/extra/save_order_detail", 'call', {
            'customer_priority': customer_priority,
            'client_order_ref': client_order_ref,
            'note': note
        }).then(function (data) {
            console.log(data);
        });
    });
    // END SAVE ORDER DETAIL ON ONCHANGE OF TEXT CONTENT

    $('#use_acc_comm').change(function() {
        if($(this).is(':checked')){
            ajax.jsonRpc("/get-contact-info", 'call').then(function (data) {
                if (data){
                    $('input[name="name"]').val(data.name);
                    $('input[name="comp_name"]').val(data.company);
                    $('input[name="street"]').val(data.street);
                    $('input[name="street2"]').val(data.street2);
                    $('input[name="city"]').val(data.city);
                    $('input[name="zip"]').val(data.zip);
                    $('input[name="email"]').val(data.email);
                    $('input[name="phone"]').val(data.phone);
                    $('input[name="alternate_communication_1"]').val(data.other_communication_1);
                    $('input[name="alternate_communication_2"]').val(data.other_communication_2);

                    $('select[name="state_id"]').val(data.state_id);
                    $('select[name="country_id"]').val(data.country_id);
                    $('select[name="primary_tel_type"]').val(data.primary_tel_type);
                    $('select[name="alternate_commu_type_1"]').val(data.other_communication_type_1);
                    $('select[name="alternate_commu_type_2"]').val(data.other_communication_type_2);
                }
            });
        }
    });

});
});
