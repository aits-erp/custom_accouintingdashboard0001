import frappe
from collections import defaultdict


def execute(filters=None):
    columns = get_columns()
    data, chart = get_data(filters)
    return columns, data, None, chart


def get_columns():
    return [
        {"label": "Parameter", "fieldname": "parameter", "fieldtype": "Data", "width": 320},
        {"label": "Qty", "fieldname": "qty", "fieldtype": "Float", "width": 120},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 200},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 200},
    ]


def get_data(filters):

    conditions = ""
    if filters.get("warehouse"):
        conditions += " AND b.warehouse = %(warehouse)s"

    if filters.get("item_group"):
        conditions += " AND i.item_group = %(item_group)s"

    items = frappe.db.sql(f"""
        SELECT
            i.item_code,
            i.item_group,
            i.custom_width,
            i.custom_weight,
            i.custom_length,
            b.warehouse,
            SUM(b.actual_qty) as qty
        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON i.item_code = b.item_code
        WHERE i.disabled = 0 {conditions}
        GROUP BY i.item_code, b.warehouse
        ORDER BY i.item_group, i.custom_width, i.custom_weight, i.custom_length
    """, filters, as_dict=True)

    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    chart_data = defaultdict(float)

    for i in items:
        tree[i.item_group][i.custom_width][i.custom_weight][i.custom_length].append(i)
        chart_data[i.item_group] += i.qty or 0

    data = []

    for group, widths in tree.items():
        group_total = 0

        for w in widths.values():
            for we in w.values():
                for l in we.values():
                    for item in l:
                        group_total += item.qty or 0

        data.append({
            "parameter": group,
            "qty": group_total,
            "indent": 0
        })

        for width, weights in widths.items():
            width_total = 0

            for we in weights.values():
                for l in we.values():
                    for item in l:
                        width_total += item.qty or 0

            data.append({
                "parameter": f"Width: {width}",
                "qty": width_total,
                "indent": 1
            })

            for weight, lengths in weights.items():
                weight_total = 0

                for l in lengths.values():
                    for item in l:
                        weight_total += item.qty or 0

                data.append({
                    "parameter": f"Weight: {weight}",
                    "qty": weight_total,
                    "indent": 2
                })

                for length, items_list in lengths.items():
                    length_total = sum(i.qty or 0 for i in items_list)

                    data.append({
                        "parameter": f"Length: {length}",
                        "qty": length_total,
                        "indent": 3
                    })

                    for i in items_list:
                        data.append({
                            "parameter": "",
                            "item_code": i.item_code,
                            "warehouse": i.warehouse,
                            "qty": i.qty,
                            "indent": 4
                        })

    chart = {
        "data": {
            "labels": list(chart_data.keys()),
            "datasets": [
                {
                    "name": "Stock Qty",
                    "values": list(chart_data.values())
                }
            ]
        },
        "type": "bar"
    }

    return data, chart
