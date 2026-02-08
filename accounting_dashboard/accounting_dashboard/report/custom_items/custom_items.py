import frappe
from frappe.utils import flt


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    total_qty = 0
    total_consume_qty = 0
    total_balance_qty = 0

    total_rolls = 0
    total_consume_rolls = 0
    total_balance_rolls = 0

    total_length = 0
    total_width = 0
    total_weight = 0

    for row in data:

        row["balance_qty"] = flt(row.get("qty")) - flt(row.get("consume_qty"))
        row["balance_rolls"] = flt(row.get("custom_rolls")) - flt(row.get("consume_rolls"))

        total_qty += flt(row.get("qty"))
        total_consume_qty += flt(row.get("consume_qty"))
        total_balance_qty += flt(row.get("balance_qty"))

        total_rolls += flt(row.get("custom_rolls"))
        total_consume_rolls += flt(row.get("consume_rolls"))
        total_balance_rolls += flt(row.get("balance_rolls"))

        total_length += flt(row.get("custom_net_length"))
        total_width += flt(row.get("custom_width"))
        total_weight += flt(row.get("custom_weight_gsm"))

    total_row = {
        "item_code": "GRAND TOTAL",
        "qty": total_qty,
        "consume_qty": total_consume_qty,
        "balance_qty": total_balance_qty,
        "custom_rolls": total_rolls,
        "consume_rolls": total_consume_rolls,
        "balance_rolls": total_balance_rolls,
        "custom_net_length": total_length,
        "custom_width": total_width,
        "custom_weight_gsm": total_weight,
    }

    data.append(total_row)

    return columns, data


# --------------------------------------------------

def get_columns():
    return [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Roll No", "fieldname": "custom_roll_no", "fieldtype": "Data", "width": 120},

        {"label": "Quantity SQM", "fieldname": "qty", "fieldtype": "Float", "width": 130},
        {"label": "Consume SQM", "fieldname": "consume_qty", "fieldtype": "Float", "width": 130},
        {"label": "Balance SQM", "fieldname": "balance_qty", "fieldtype": "Float", "width": 130},

        {"label": "Rack", "fieldname": "custom_rack", "fieldtype": "Data", "width": 120},
        {"label": "Colour Code", "fieldname": "custom_colour_code", "fieldtype": "Data", "width": 120},
        {"label": "Weight GSM", "fieldname": "custom_weight_gsm", "fieldtype": "Float", "width": 120},
        {"label": "Width", "fieldname": "custom_width", "fieldtype": "Float", "width": 120},
        {"label": "Net Length", "fieldname": "custom_net_length", "fieldtype": "Float", "width": 120},

        {"label": "Rolls", "fieldname": "custom_rolls", "fieldtype": "Float", "width": 100},
        {"label": "Consume Rolls", "fieldname": "consume_rolls", "fieldtype": "Float", "width": 130},
        {"label": "Balance Rolls", "fieldname": "balance_rolls", "fieldtype": "Float", "width": 130},
    ]


# --------------------------------------------------

def get_conditions(filters):
    conditions = ""

    if filters.get("item_code"):
        conditions += " AND pri.item_code = %(item_code)s"

    if filters.get("roll_no"):
        filters["roll_no"] = f"%{filters['roll_no']}%"
        conditions += " AND pri.custom_roll_no LIKE %(roll_no)s"

    if filters.get("rack"):
        filters["rack"] = f"%{filters['rack']}%"
        conditions += " AND pri.custom_rack LIKE %(rack)s"

    if filters.get("colour_code"):
        filters["colour_code"] = f"%{filters['colour_code']}%"
        conditions += " AND pri.custom_colour_code LIKE %(colour_code)s"

    if filters.get("weight_gsm"):
        conditions += " AND pri.custom_weight_gsm = %(weight_gsm)s"

    if filters.get("width"):
        conditions += " AND pri.custom_width = %(width)s"

    if filters.get("net_length"):
        conditions += " AND pri.custom_net_length = %(net_length)s"

    if filters.get("from_date"):
        conditions += " AND pr.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND pr.posting_date <= %(to_date)s"

    return conditions


# --------------------------------------------------

def get_data(filters):

    conditions = get_conditions(filters)

    query = f"""
        SELECT
            pri.item_code,
            pri.custom_roll_no,
            pri.qty,
            pri.custom_rack,
            pri.custom_colour_code,
            pri.custom_weight_gsm,
            pri.custom_width,
            pri.custom_net_length,
            pri.custom_rolls,

            IFNULL(SUM(dni.qty), 0) as consume_qty,
            IFNULL(SUM(dni.custom_rolls), 0) as consume_rolls

        FROM `tabPurchase Receipt Item` pri
        INNER JOIN `tabPurchase Receipt` pr
            ON pr.name = pri.parent

        LEFT JOIN `tabDelivery Note Item` dni
            ON dni.item_code = pri.item_code
            AND dni.custom_roll_no = pri.custom_roll_no
            AND dni.docstatus = 1

        WHERE pr.docstatus = 1
        {conditions}

        GROUP BY pri.name
        ORDER BY pr.posting_date DESC
    """

    return frappe.db.sql(query, filters, as_dict=1)
