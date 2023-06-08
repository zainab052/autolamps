# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Point Of Sale - Order Analysis",
    "version": "8.0.1.0.0",
    "category": "Point Of Sale",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "point_of_sale"
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "reports/pos_order_analysis.xml"
    ],
}
