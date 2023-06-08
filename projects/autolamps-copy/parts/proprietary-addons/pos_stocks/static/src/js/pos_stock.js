/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
openerp.pos_stocks = function(instance, module) {
    module = instance.point_of_sale;
    _t = instance.web._t;
    var round_pr = instance.web.round_precision
    var _initialize_ = module.PosModel.prototype.initialize;
    var SuperPosModel = module.PosModel;
    var models = SuperPosModel.prototype.models;

    for(var i = 0; i < models.length; i++){
		var model = models[i];
		if(model.model === 'product.product'){
            model.fields.push('qty_available','virtual_available','outgoing_qty','type')
            model.context = function(self){ 
                    return { pricelist: self.pricelist.id, display_default_code: false ,location: self.config.stock_location_id[0]};
                }
			//--loading product price by pricelist ------
			var super_product_loaded = model.loaded;
            model.loaded = function(self,products){

                if(self.config.wk_display_stock && self.config.wk_hide_out_of_stock){
                    var available_product = [];
                    for(var i = 0,len = products.length; i<len; i++){
                        switch(self.config.wk_stock_type){
                            case'forecasted_qty':
                                if(products[i].virtual_available>0||products[i].type == 'service')
                                    available_product.push(products[i]);
                                break;
                            case'virtual_qty':
                                if((products[i].qty_available-products[i].outgoing_qty)>0||products[i].type == 'service')
                                    available_product.push(products[i]);
                                break;
                            default:
                                if(products[i].qty_available>0||products[i].type == 'service')
                                    available_product.push(products[i]);
                        }
                    }
                    products = available_product;
                }

                var results={}
                for(var i = 0,len=products.length;i<len;i++){
                    switch(self.config.wk_stock_type){
                        case'available_qty':
                            results[products[i].id]=products[i].qty_available
                            break;
                        case'forecasted_qty':
                            results[products[i].id]=products[i].virtual_available
                            break;
                        default:
                            results[products[i].id]=products[i].qty_available-products[i].outgoing_qty
                    }
                }
                self.set({'wk_product_qtys' : results});
                self.pos_widget.wk_change_qty_css()
                super_product_loaded.call(this,self,products);
            }
        }	
    }

    module.OutOfStockMessagePopup = module.PopUpWidget.extend({
        template:'OutOfStockMessagePopup',
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
        }
    });

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
				//orderline.set_unit_price(product.list_price);
				orderline.stock_location_id = location_id;
				orderline.set_quantity(entered_qty);
				orderline.comment = 1.0;


				var pricelist_value = null;
                var pricelist_id = parseInt($('#price_list').val()) || this.pos.config.pricelist_id[0];

				new instance.web.Model("product.pricelist").get_func('price_get')([pricelist_id], product.id, entered_qty).pipe(
                    function(res){
                        if (res[pricelist_id]) {
                            pricelist_value = parseFloat(res[pricelist_id].toFixed(2));
                            if (pricelist_value) {
                                orderline.set_unit_price(pricelist_value);

                                order.get('orderLines').add(orderline);
                                order.selectLine(order.getLastOrderline());
                                self.pos.pos_widget.screen_selector.close_popup();
                            }
                            else {
                                orderline.set_unit_price(product.list_price);

                                order.get('orderLines').add(orderline);
                                order.selectLine(order.getLastOrderline());
                                self.pos.pos_widget.screen_selector.close_popup();
                            }
                        }
                    }
                );
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
            this.out_of_stock_popup = new module.OutOfStockMessagePopup(this, {});
            this.out_of_stock_popup.appendTo(this.$el);
            this.out_of_stock_popup.hide();
            this.screen_selector.popup_set['out_of_stock'] = this.out_of_stock_popup;

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

    var PosModelSuper = module.PosModel
    module.PosModel = module.PosModel.extend({
        push_and_invoice_order: function(order) {
            var self = this;
            if (order != undefined) {
                if(!order.is_return_order){
                    var wk_order_line = order.get('orderLines');
                    for (var j = 0; j < wk_order_line.length; j++) {
                        if(!wk_order_line.models[j].stock_location_id)
                            self.get('wk_product_qtys')[wk_order_line.models[j].product.id] = self.get('wk_product_qtys')[wk_order_line.models[j].product.id] - wk_order_line.models[j].quantity;
                    }
                }
                else{
                    var wk_order_line = order.get('orderLines');
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line.models[j].product.id] = self.get('wk_product_qtys')[wk_order_line.models[j].product.id] + wk_order_line.models[j].quantity;
                    }
                }
            }
            var push = PosModelSuper.prototype.push_and_invoice_order.call(this, order);
            return push;
        },

        push_order: function(order) {
            var self = this;
            if (order != undefined) {
               if(!order.is_return_order){
                    var wk_order_line = order.get('orderLines');
                    for (var j = 0; j < wk_order_line.length; j++) {
                        if(!wk_order_line.models[j].stock_location_id)
                            self.get('wk_product_qtys')[wk_order_line.models[j].product.id] = self.get('wk_product_qtys')[wk_order_line.models[j].product.id] - wk_order_line.models[j].quantity;
                    }
                }
                else{
                    var wk_order_line = order.get('orderLines');
                    for (var j = 0; j < wk_order_line.length; j++) {
                        self.get('wk_product_qtys')[wk_order_line.models[j].product.id] = self.get('wk_product_qtys')[wk_order_line.models[j].product.id] + wk_order_line.models[j].quantity;
                    }
                }
            }

            var push = PosModelSuper.prototype.push_order.call(this, order);
            return push;
        },
    });

    module.PosBaseWidget.include({
        get_information: function(wk_product_id) {
            var self = this;
            return self.pos.get('wk_product_qtys')[wk_product_id];
        },
        set_stock_qtys: function(result){
            var self = this;
            if(!self.pos.pos_widget.screen_selector){
                $.unblockUI();
                return;
            }
            self.pos.pos_widget.product_screen.product_categories_widget.reset_category();
            var all = $('.product');
            $.each(all, function(index, value){
                var product_id = $(value).data('product-id');
                var stock_qty = result[product_id];
                $(value).find('.qty-tag').html(stock_qty);
            });
            $.unblockUI();
        },

        wk_change_qty_css: function() {
            var self = this;
            var wk_order = self.pos.get('orders');
            var wk_p_qty = new Array();
            var wk_product_obj = self.pos.get('wk_product_qtys');
            for (var i in wk_product_obj) {
                wk_p_qty[i] = self.pos.get('wk_product_qtys')[i];
            }
            for (i = 0; i < wk_order.length; i++) {
                if(!wk_order.models[i].is_return_order){
                    var wk_order_line = wk_order.models[i].get('orderLines')
                    for (j = 0; j < wk_order_line.length; j++) {
                        if(!wk_order_line.models[j].stock_location_id) 
                            wk_p_qty[wk_order_line.models[j].product.id] = wk_p_qty[wk_order_line.models[j].product.id] - wk_order_line.models[j].quantity;                                     
                        $("#qty-tag" + wk_order_line.models[j].product.id).html(wk_p_qty[wk_order_line.models[j].product.id]);
                    }
                }
            }
        },
        check_product_qty: function(product_id) {
			var self = this;
			var wk_order = self.pos.get('orders');
			var wk_p_qty = new Array();
			var qty;
			var wk_product_obj = self.pos.get('wk_product_qtys');
			if (wk_order) {
				for (var i in wk_product_obj)
					wk_p_qty[i] = self.pos.get('wk_product_qtys')[i];
				_.each(wk_order.models,function(order){
                    var orderline = order.get('orderLines').models
					if(orderline.length > 0)
						_.each(orderline, function(line){
							if(!line.stock_location_id && product_id == line.product.id)
								wk_p_qty[line.product.id] = wk_p_qty[line.product.id] - line.quantity;
						})
				})
				qty = wk_p_qty[product_id];
			}
			return qty
		}
    });

    var PosOrderSuper = module.Order
    module.Order = module.Order.extend({
        template: 'Order',
        addProduct: function(product, options) {
            var self = this;
            var avilable_qty =  this.pos.get('wk_product_qtys')[product.id];
            if (!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && !self.pos.get_order().is_return_order) {
                var qty_count = 0;
				if(parseInt($("#qty-tag" + product.id).html()))
                    qty_count = parseInt($("#qty-tag" + product.id).html())
				else{
                    qty_count = self.pos.pos_widget.check_product_qty(product.id)
                }

                if(options != undefined && options.from_order_load){
                    PosOrderSuper.prototype.addProduct.call(this, product, options);
                } else {
                    if (qty_count <= self.pos.config.wk_deny_val) {
                        self.pos.pos_widget.screen_selector.show_popup('out_of_stock', {
                            'message': _t("Warning !!!!"),
                            'body': _t("(" + product.display_name + ") " + self.pos.config.wk_error_msg + "."),
                            'product_id':product.id,
                        });
                    } else {
                        PosOrderSuper.prototype.addProduct.call(this, product, options);
                    }
                }

            } else {
                PosOrderSuper.prototype.addProduct.call(this, product, options);
            }
            if (self.pos.config.wk_display_stock && !self.pos.get_order().is_return_order) {
                self.pos.pos_widget.wk_change_qty_css();
            }
        },
    });

    module.ScreenWidget.include({
		barcode_product_action: function(code){
			var self = this;
			var product =  this.pos.db.get_product_by_ean13(code.base_code);
			if(product){
				var qty_count = 0;
				if(parseInt($("#qty-tag" + product.id).html()))
					qty_count = parseInt($("#qty-tag" + product.id).html())
				else
					qty_count = self.pos.pos_widget.check_product_qty(product.id)
                
				if (qty_count <= self.pos.config.wk_deny_val)
                    self.pos.pos_widget.screen_selector.show_popup('out_of_stock', {
                        'message': _t("Warning !!!!"),
                        'body': _t("(" + product.display_name + ") " + self.pos.config.wk_error_msg + "."),
                        'product_id':product.id,
                    });
				else
					self._super(code);
			}else
				self._super(code);
		},
	});

    module.ProductScreenWidget = module.ProductScreenWidget.extend({
        show: function(){
            var self = this;
            this._super();
            self.pos.pos_widget.set_stock_qtys(self.pos.get('wk_product_qtys'));
            self.pos.pos_widget.wk_change_qty_css();
        },
    });

    var PosOrderlineSuper = module.Orderline
    module.Orderline = module.Orderline.extend({
        template: 'Orderline',
        set_quantity: function(quantity) {
            var self = this;
            if(self.stock_location_id && quantity && quantity!='remove'){
                if(self.pos.get_order() &&  self.pos.get_order().selected_orderline &&  self.pos.get_order().selected_orderline.cid == self.cid){
                   
                    self.pos.pos_widget.screen_selector.show_popup('out_of_stock', {
                        'message': _t("Warning !!!!"),
                        'body': _t("Selected orderline product have different stock location, you can't update the qty of this orderline"),
                        'product_id':self.product.id
                    });
                    return ;
                }
                else{
                    PosOrderlineSuper.prototype.set_quantity.call(this, quantity);     
                    return;
                    
                }   
            }
            if (this.pos.get('selectedOrder').getSelectedLine() != undefined && quantity !=='remove' && quantity!== '') {
                if(this.pos.get('selectedOrder').getSelectedLine().product.id == self.product.id && self.product.type != 'service'){
                    var present_line = self.pos.get('selectedOrder').getSelectedLine();
                    var avilable_qty = self.pos.get('wk_product_qtys')[present_line.product.id];
                    var added_qty = present_line.quantity;
                    var allow_order = self.pos.config.wk_continous_sale;
                    var allow_quantity = avilable_qty - self.pos.config.wk_deny_val;

                    if((added_qty <= allow_quantity && parseFloat(quantity) <= allow_quantity)|| allow_order) {
                        PosOrderlineSuper.prototype.set_quantity.call(this, quantity);
                        if (this.pos.config.wk_display_stock) {
                            this.pos.pos_widget.wk_change_qty_css();
                        }
                    }
                    else {
                        this.pos.pos_widget.screen_selector.show_popup('out_of_stock', {
                            'message': _t("Warning !!!!"),
                            'body': _t("(" + (this.pos.get('selectedOrder')).getSelectedLine().product.display_name + ") " + this.pos.config.wk_error_msg + "."),
                            'product_id':this.pos.get('selectedOrder').getSelectedLine().product.id,
                        });
                        // If we already have items in order line, don't reset
                        //$('.numpad-backspace').trigger("click");
                    }
                }
                else{
                    PosOrderlineSuper.prototype.set_quantity.call(this, quantity);     
                }
            }
            else if(quantity === 'remove') {
                var present_line = this.pos.get('selectedOrder').getSelectedLine();
                PosOrderlineSuper.prototype.set_quantity.call(this, quantity);
                if (!present_line.stock_location_id)
                    $("#qty-tag" + present_line.product.id).html(this.pos.get('wk_product_qtys')[present_line.product.id]);
            }
            else {
                PosOrderlineSuper.prototype.set_quantity.call(this, quantity);
                if (this.pos.config.wk_display_stock) {
                    this.pos.pos_widget.wk_change_qty_css();
                }
            }
        },

        export_as_JSON: function() {
			var self = this;
			var loaded = PosOrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
			loaded.stock_location_id = self.stock_location_id;
			return loaded;
		},
    });
}