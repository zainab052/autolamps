openerp.pos_pricelist_aces = function (instance, module) {
    module = instance.point_of_sale
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;

    module.PosModel.prototype.models.push({
        model:  'product.pricelist',
        fields: [],
        domain: [['type', '=', 'sale']],
        loaded: function(self, prod_pricelists){
            self.prod_pricelists = [];
            self.prod_pricelists = prod_pricelists;
        },
    });

    var _super_ProductScreenWidget = module.ProductScreenWidget.prototype
    module.ProductScreenWidget = module.ProductScreenWidget.extend({
        init: function() {
            this._super.apply(this, arguments);
        },
        start:function(){
            var self = this;
            _super_ProductScreenWidget.start.call(this);
            pos = self.pos;
            selectedOrder = self.pos.get('selectedOrder');

            var pricelist_list = self.pos.prod_pricelists;
            var new_options = [];
            new_options.push('<option value="">Select Pricelist</option>\n');
            if(pricelist_list.length > 0){
                for(var i = 0, len = pricelist_list.length; i < len; i++){
                    new_options.push('<option value="' + pricelist_list[i].id + '">' + pricelist_list[i].display_name + '</option>\n');
                }
                $('#price_list').html(new_options);
                $('#price_list').selectedIndex = 0;

                // Always Set default PriceList
                $('#price_list').val(self.pos.config.pricelist_id[0]);

            }

//            $('#price_list').on('change', function() {
//                var partner_id = self.pos.get('selectedOrder').get_client() && parseInt(self.pos.get('selectedOrder').get_client().id);
//                if (!partner_id) {
//                    $('#price_list').val(' ');
//                    alert('Pricelist will not work as customer is not selected !');
//                    return;
//                }
//            });
        },
    });
    
    var _super_ReceiptScreenWidget = module.ReceiptScreenWidget.prototype;
    module.ReceiptScreenWidget = module.ReceiptScreenWidget.extend({
        finishOrder: function() {
            // Set it back to the default price_list
            $('#price_list').val(this.pos.config.pricelist_id[0]);
            _super_ReceiptScreenWidget.finishOrder.call(this);
        },
    });

    var PosOrderSuper = module.Order;
    module.Order = module.Order.extend({
        set_pricelist_val: function(client_id) {
            var self = this;
            if (client_id) {
                new instance.web.Model("res.partner").get_func("read")(parseInt(client_id), ['property_product_pricelist']).pipe(
                    function(result) {
                        if (result && result.property_product_pricelist) {
                            self.set('pricelist_val', result.property_product_pricelist[0] || '');
                            $('#price_list').val(result.property_product_pricelist[0]);
                        }
                    }
                );
            }
        },
        get_pricelist: function() {
            return this.get('pricelist_val');
        },
        addProduct: function(product, options){
            var self = this;
            var pricelist_id = parseInt($('#price_list').val()) || this.pos.config.pricelist_id[0];
            if (pricelist_id) {

                var avilable_qty =  this.pos.get('wk_product_qtys')[product.id];
                var qty_count = 0;
				if(parseInt($("#qty-tag" + product.id).html()))
                    qty_count = parseInt($("#qty-tag" + product.id).html())
				else{
                    qty_count = self.pos.pos_widget.check_product_qty(product.id)
                }


                if (qty_count <= self.pos.config.wk_deny_val) {
                    PosOrderSuper.prototype.addProduct.call(this, product, options);
                }else{
                    if(this._printed){
                        this.destroy();
                        return this.pos.get('selectedOrder').addProduct(product, options);
                    }
                options = options || {};
                var attr = JSON.parse(JSON.stringify(product));
                attr.pos = this.pos;
                attr.order = this;
                var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});

                if(options.quantity !== undefined){
                    line.set_quantity(options.quantity);
                }
                if(options.price !== undefined){
                    line.set_unit_price(options.price);
                }
                if(options.discount !== undefined){
                    line.set_discount(options.discount);
                }

                var last_orderline = this.getLastOrderline();
                if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                    last_orderline.merge(line);
                    var qty = last_orderline.get_quantity();
                    new instance.web.Model("product.pricelist").get_func('price_get')([pricelist_id], product.id, qty).pipe(
                            function(res){
                                if (res[pricelist_id]) {
                                    pricelist_value = parseFloat(res[pricelist_id].toFixed(2));
                                    if (pricelist_value) {
                                        last_orderline.set_unit_price(pricelist_value);
                                    }
                                }
                            }
                        );
                } else {
                    var pricelist_value = null;
                    var self = this;
                    new instance.web.Model("product.pricelist").get_func('price_get')([pricelist_id], product.id, 1).pipe(
                        function(res){
                            if (res[pricelist_id]) {
                                pricelist_value = parseFloat(res[pricelist_id].toFixed(2));
                                if (pricelist_value) {
                                    line.set_unit_price(pricelist_value);
                                    self.get('orderLines').add(line);
                                    self.selectLine(self.getLastOrderline());
                                }
                                else {
                                    self.get('orderLines').add(line);
                                    self.selectLine(self.getLastOrderline());
                                }
                            }
                        }
                    );
                }
                this.selectLine(this.getLastOrderline());
                }


            } else {
                PosOrderSuper.prototype.addProduct.call(this, product, options);
            }
        },
    });

    var _super_OrderWidget = module.OrderWidget.prototype;
    module.OrderWidget = module.OrderWidget.extend({
        set_value: function(val) {
            var res = _super_OrderWidget.set_value.call(this, val);
            var order = this.pos.get('selectedOrder');
            if (this.editable && order.getSelectedLine()) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity'){
                    var partner_id = order.get_client() && parseInt(order.get_client().id);
                    var pricelist_id = parseInt($('#price_list').val()) || parseInt(order.get_pricelist());
                    if ((val != 'remove') && pricelist_id && order && order.getSelectedLine().get_product().id) {
                        var p_id = order.getSelectedLine().get_product().id;
                        new instance.web.Model("product.pricelist").get_func('price_get')([pricelist_id], p_id, parseInt(val)).pipe(
                            function(res){
                                if (res && res[pricelist_id]) {
                                    pricelist_value = parseFloat(res[pricelist_id].toFixed(2));
                                    if (pricelist_value && order.getSelectedLine()) {
                                        order.getSelectedLine().set_quantity(val);
                                        order.getSelectedLine().set_unit_price(pricelist_value);
                                    }
                                }
                            }
                        );
                    } else {
                        return res;
                    }
                }
            }
        },
    });
    
    var _super_PosModel = module.PosModel.prototype;
    module.PosModel = module.PosModel.extend({
        //removes the current order
        delete_current_order: function(){
            _super_PosModel.delete_current_order.call(this);
            $('#price_list').val(this.get('selectedOrder').get_pricelist());
        },
    });
    
    var _super_OrderButtonWidget = module.OrderButtonWidget.prototype;
    module.OrderButtonWidget = module.OrderButtonWidget.extend({
        selectOrder: function(event) {
            _super_OrderButtonWidget.selectOrder.call(this, event);
            if(this.order.get_client()){
                this.order.set_pricelist_val(this.order.get_client().id);
                $('#price_list').val(this.order.get_pricelist());
            } else {
                $('#price_list').val(this.pos.config.pricelist_id[0]);
            }
        },
    });
    
    var _super_ClientListScreenWidget = module.ClientListScreenWidget.prototype;
    module.ClientListScreenWidget = module.ClientListScreenWidget.extend({
        save_changes: function(){
            _super_ClientListScreenWidget.save_changes.call(this);
            if( this.has_client_changed() ){
                this.pos.get('selectedOrder').set_pricelist_val(this.new_client.id);
            }
        },
    });

}