# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Warehouse Management",
  "summary"              :  """The module allows the POS user to manage multiple warehouses in the POS. If a product goes out of stock at one warehouse, the user can place the order from other warehouse.""",
  "category"             :  "Point of Sale",
  "version"              :  "1.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Warehouse-Management.html",
  "description"          :  """Odoo POS Warehouse Management
POS manage multiple warehouses
POS out of stock
Out-of-stock products
POS select multiple warehouse
Order from multiple warehouse POS
Show other warehouses POS""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_warehouse_management",
  "depends"              :  [
                             'point_of_sale',
                             'pos_stocks',
                            ],
  "data"                 :  [
                             'views/pos_warehouse_management_view.xml',
                             'views/template.xml',
                            ],
  "qweb"                 :  ['static/src/xml/pos_warehouse_management.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}