from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare

class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'sold_ok': fields.boolean('Sold', help="Specify if the product can be selected in a sales order line."),
    }
