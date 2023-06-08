/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
openerp.pos_extra_utilities = function(instance){
	var module   = instance.point_of_sale;
	var SuperPosWidget = module.PosWidget.prototype;
	var QWeb = instance.web.qweb;
	_t = instance.web._t;

	var PriceUpdatePopupWidget = module.PopUpWidget.extend({
		template:'PriceUpdatePopupWidget',
		show: function(options){
			$('#price_error').hide();
			var self = this;
			this._super(options);
			$("#wk_ok").on('click',function(){
				var previous_price = self.pos.get_order().selected_orderline.price;
				var new_price = $("#price_input").val();
				if(!$.isNumeric(new_price))
				{
					$('#price_error').show();
					$('#price_error').addClass("fa fa-warning");
					$('#price_error').text("  Please enter a numeric value");
				}
				else if(parseFloat(new_price)<parseFloat(previous_price))
				{
					$('#price_error').show();
					$('#price_error').addClass("fa fa-warning");
					$('#price_error').text("  New price must be greater than current price");
				}
				else
				{ 
					self.pos_widget.numpad.state.resetValue();
					self.pos_widget.numpad.state.appendNewChar(new_price);
					self.pos_widget.screen_selector.close_popup();
					setTimeout(function(){
						self.pos_widget.numpad.state.reset();
					},500);
				}
			});
			if(self.pos.get_order().selected_orderline != null)
			{
				self.$('td#selected_product_name').text(self.pos.get_order().selected_orderline.product.display_name);
				self.$('textarea#price_input').val(self.pos.get_order().selected_orderline.get_unit_price());
			}
			$("#wk_cancel").on('click',function(){
				self.pos_widget.numpad.state.reset();
				self.pos_widget.screen_selector.close_popup();
			});
		}
	});

	module.PosWidget = module.PosWidget.extend({
		start: function() {
			var self = this;
			SuperPosWidget.start.call(this);
			return self.pos.ready.done(function() {
				self.$('#add_note').click(function()
				{
					if(typeof(self.pos.get_order().getSelectedLine())=='object')
					{
						self.pos_widget.screen_selector.show_popup('price_update',{});
						return;
					}	
					else
						alert('Please add/select an orderline');
				});
			});
		},
		
		build_widgets: function(){
			this._super();
			var self = this;
			this.price_update = new PriceUpdatePopupWidget(this, {});
			this.price_update.appendTo(this.$el);
			this.price_update.hide();
			this.screen_selector.popup_set['price_update'] = this.price_update;
		},
	});

	module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
		validate_order: function(options) {
			var self = this;
			var order = this.pos.get_order();
			
			if (self.pos.config.validation_check) 
			{	
				if(order.get_client()==null)
				{
					if(order.get_client()==null)
					{
						self.pos_widget.screen_selector.show_popup('error',{
							message: _t('An anonymous order cannot be validated'),
							comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
						});
					}
				}
				else
					this._super();
			}else
				this._super();
		}
	});

	module.NumpadWidget.include({
		clickChangeMode: function(event) {
			var self = this;
			var previous_mode = $('.selected-mode').attr('data-mode');
			var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
			if(self.pos.config.disable_price_modification && newMode=='price')
					newMode =previous_mode;
			if(self.pos.config.disable_discount_button && newMode=='discount')
					newMode =previous_mode;
			return this.state.changeMode(newMode);
		},
		changedMode: function() {
			var self = this;
			var mode = this.state.get('mode');
			$('.selected-mode').removeClass('selected-mode');
			$(_.str.sprintf('.mode-button[data-mode="%s"]', mode), this.$el).addClass('selected-mode');
			if(self.pos.config.allow_only_price_increase && mode == 'price')
			{
				if(self.pos.get_order().selected_orderline)
				{	
					self.pos_widget.screen_selector.show_popup('price_update',{});
				}
			}
		}
	});
}