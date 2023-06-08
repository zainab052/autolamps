/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
openerp.pos_warehouse_management = function(instance){
	var module   = instance.point_of_sale;
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	var SuperOrderline = module.Orderline.prototype;

	module.ProductStockPopup = module.PopUpWidget.extend({
        template:'ProductStockPopup',

		events:{
			'click .button.cancel': 'click_cancel',
			'click .stock_line' : 'click_stock_location_line',
			'click .button.apply'  :'wk_add_product_to_orderline'
		},

		click_cancel: function(){
			this.pos.pos_widget.screen_selector.close_popup()
		},

        show: function(options){
            this.options = options;
            this._super();
             this.renderElement();
        },
		
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.button.cancel').on('click',function(){
                self.pos.pos_widget.screen_selector.close_popup();
            });
        },
		
		click_stock_location_line: function(event){
			var self = this;
			var id = $(event.target).parent().data('line-id')
			this.stock_line_select(event,$(event.target),id);
		},

		stock_line_select: function(event,$line,id){

			if ($line.parent().hasClass('selected')){
				$line.parent().removeClass('selected');
				event.target.parentNode.style.backgroundColor = '';
				this.$('.product_qty').css('display','none');
			}
			else{
				this.$('.stock_line.selected').css('background-color','');
				this.$('.stock_line.selected').removeClass('selected');
				$line.parent().addClass('selected');
				event.target.parentNode.style.backgroundColor = '#6EC89B'
				this.$('.product_qty').css('display','block');
				this.$('#qty_input').focus()
			}
    	},

		wk_add_product_to_orderline: function() {
			var self = this;
			var availabe_qty = parseInt(this.$('.stock_line.selected').find('.available_qty').text())
			var entered_qty = parseFloat(this.$('.product_qty').find('#qty_input').val())
			var order = self.pos.get_order();
			var location_id = this.$('.stock_line.selected').data('line-id')
			var product = self.pos.db.product_by_id[self.options.product_info[0]]

			if(! $('.stock_line.selected').length){
				$("stock_line").css("background-color","burlywood");
				setTimeout(function(){
					$(".stock_line").css("background-color","");
				},100);
				setTimeout(function(){
					$(".stock_line").css("background-color","burlywood");
				},200);
				setTimeout(function(){
					$(".stock_line").css("background-color","");
				},300);
				setTimeout(function(){
					$(".stock_line").css("background-color","burlywood");
				},400);
				setTimeout(function(){
					$(".stock_line").css("background-color","");
				},500);
				this.$('.stock_line').focus()
				return;
			}
				
			else if(availabe_qty >= entered_qty && entered_qty > 0){
				$('.stock_line.selected').removeClass('selected');
				var orderline = new module.Orderline({}, {
					pos: self.pos,
					order: order,
					product: product,
					stock_location_id:location_id,
					availabe_qty: availabe_qty,
				});
				orderline.product = product;
				orderline.set_unit_price(product.list_price);
				orderline.stock_location_id = location_id;
				orderline.set_quantity(entered_qty);
				orderline.comment = 1.0;
				order.get('orderLines').add(orderline);
				order.selectLine(order.getLastOrderline());
				self.pos.pos_widget.screen_selector.close_popup();
			}
			else
			{
				$("#qty_input").css("background-color","burlywood");
				setTimeout(function(){
					$("#qty_input").css("background-color","");
				},100);
				setTimeout(function(){
					$("#qty_input").css("background-color","burlywood");
				},200);
				setTimeout(function(){
					$("#qty_input").css("background-color","");
				},300);
				setTimeout(function(){
					$("#qty_input").css("background-color","burlywood");
				},400);
				setTimeout(function(){
					$("#qty_input").css("background-color","");
				},500);
				this.$('#qty_input').focus()
				return;
			}
		},
	});
	
	var NoRelatedStockLocationPopup = module.PopUpWidget.extend({
		template:'NoRelatedStockLocationPopup',
		events:{
			'click .button.cancel': 'click_cancel',
		},
		show: function(options){
            this.options = options;
            this._super();
             this.renderElement();
		},
		click_cancel:function(){
			this.pos.pos_widget.screen_selector.close_popup();
		}
	});

    module.PosWidget.include({
		build_widgets: function(){
			var self = this;
			this._super();    
			this.product_stock_popup = new module.ProductStockPopup(this, {});
			this.product_stock_popup.appendTo(this.$el);
			this.product_stock_popup.hide();
			this.screen_selector.popup_set['product_stock'] = this.product_stock_popup;
			this.no_related_stock_locations = new NoRelatedStockLocationPopup(this, {});
			this.no_related_stock_locations.appendTo(this.$el);
			this.no_related_stock_locations.hide();
			this.screen_selector.popup_set['no_related_stock_locations'] = this.no_related_stock_locations;
		},
	});


	module.OutOfStockMessagePopup.include({
	events : {
			'click .button.show_other_stocks': 'show_other_stock_locations',
			'click .button.cancel': 'click_cancel',
		},

		click_cancel: function(){
			this.pos.pos_widget.screen_selector.close_popup();
		},

		show_other_stock_locations: function() {
			var self =this;
			if (self.pos.config.related_stock_location_ids.length){
				(new instance.web.Model('product.product')).call('get_product_stock_info',[{
					'location_ids' : self.pos.config.related_stock_location_ids,
					'pricelist_id': self.pos.pricelist.id,
					'product_id': self.options.product_id,
					'stock_type': self.pos.config.wk_stock_type,
				}])
				.then(function(result) {
					if (result) {
						self.pos.pos_widget.screen_selector.show_popup('product_stock',{
						'stock_info'  : result,
						'product_info': [self.options.product_id,self.pos.db.product_by_id[self.options.product_id].display_name]
						});
					}
					else{
						self.$('.body').html("Product is  unavailable in other related stock locations")
						self.$('.button.show_other_stocks').css('display','none');
				}
				}).fail(function(unused, event) {
					self.pos.pos_widget.screen_selector.show_popup('error',{
						'message':_t('Failed To Load Stock Locations.'),
						'comment':_t('Please make sure you are connected to the network.'),
					});
					event.preventDefault();
				});
			}
			else{
				self.pos.pos_widget.screen_selector.show_popup('no_related_stock_locations');
			}
		},
		
		show: function(options){
			var self = this;
			this.options = options || ''; 
			self._super(options);
		}
	});

	module.Orderline = module.Orderline.extend({
		export_as_JSON: function() {
			var self = this;
			var loaded=SuperOrderline.export_as_JSON.call(this);
			loaded.stock_location_id=self.stock_location_id;
			return loaded;
		},
	});
}