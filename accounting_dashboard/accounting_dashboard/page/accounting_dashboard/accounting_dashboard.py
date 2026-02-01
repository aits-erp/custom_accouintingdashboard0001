import frappe
from frappe.utils import flt, nowdate, date_diff


@frappe.whitelist()
def get_dashboard_data(from_date=None, to_date=None, company=None):

    filters = "WHERE docstatus = 1"
    if company:
        filters += f" AND company = '{company}'"
    if from_date and to_date:
        filters += f" AND posting_date BETWEEN '{from_date}' AND '{to_date}'"

    # ================= KPI =================
    sales = frappe.db.sql(f"SELECT SUM(grand_total) FROM `tabSales Invoice` {filters}")[0][0] or 0
    purchase = frappe.db.sql(f"SELECT SUM(grand_total) FROM `tabPurchase Invoice` {filters}")[0][0] or 0
    profit = flt(sales) - flt(purchase)
    margin = (profit / sales * 100) if sales else 0

    # ================= Pending Sales =================
    pending = frappe.db.sql(f"""
        SELECT customer, SUM(grand_total) as total
        FROM `tabSales Order`
        {filters} AND per_delivered < 100
        GROUP BY customer
        ORDER BY total DESC
        LIMIT 10
    """, as_dict=True)

    pending_labels = [d.customer for d in pending] or ["No Pending"]
    pending_values = [d.total for d in pending] or [0]

    # ================= Stock Bar =================
    stock = frappe.db.sql("""
        SELECT item_code, SUM(actual_qty) as qty
        FROM `tabBin`
        GROUP BY item_code
        ORDER BY qty DESC
        LIMIT 10
    """, as_dict=True)

    stock_labels = [d.item_code for d in stock] or ["No Stock"]
    stock_values = [d.qty for d in stock] or [0]

    # ================= Pie Top vs Bottom =================
    top = frappe.db.sql("""
        SELECT SUM(actual_qty)
        FROM (SELECT actual_qty FROM `tabBin` ORDER BY actual_qty DESC LIMIT 100) x
    """)[0][0] or 0

    bottom = frappe.db.sql("""
        SELECT SUM(actual_qty)
        FROM (SELECT actual_qty FROM `tabBin` ORDER BY actual_qty ASC LIMIT 100) x
    """)[0][0] or 0

    # ================= Sales Trend =================
    trend = frappe.db.sql(f"""
        SELECT DATE(posting_date) as day,
               SUM(grand_total) as total
        FROM `tabSales Invoice`
        {filters}
        GROUP BY DATE(posting_date)
        ORDER BY day
    """, as_dict=True)

    trend_labels = [str(d.day) for d in trend] or ["No Data"]
    trend_values = [d.total for d in trend] or [0]

    # ================= Customer Contribution =================
    customers = frappe.db.sql(f"""
        SELECT customer, SUM(grand_total) as total
        FROM `tabSales Invoice`
        {filters}
        GROUP BY customer
        ORDER BY total DESC
        LIMIT 5
    """, as_dict=True)

    cust_labels = [d.customer for d in customers] or ["No Data"]
    cust_values = [d.total for d in customers] or [0]

    # ================= Product Sales by Item Group =================
    items = frappe.db.sql("""
        SELECT item_group, SUM(base_net_amount) as total
        FROM `tabSales Invoice Item`
        WHERE docstatus = 1
        GROUP BY item_group
        ORDER BY total DESC
        LIMIT 5
    """, as_dict=True)

    item_labels = [d.item_group for d in items] or ["No Data"]
    item_values = [d.total for d in items] or [0]

    # ================= Aging Dashboard =================
    aging = frappe.db.sql("""
        SELECT outstanding_amount, posting_date
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND outstanding_amount > 0
    """, as_dict=True)

    buckets = {"0-30": 0, "30-60": 0, "60-90": 0, "90+": 0}

    for row in aging:
        days = date_diff(nowdate(), row.posting_date)

        if days <= 30:
            buckets["0-30"] += row.outstanding_amount
        elif days <= 60:
            buckets["30-60"] += row.outstanding_amount
        elif days <= 90:
            buckets["60-90"] += row.outstanding_amount
        else:
            buckets["90+"] += row.outstanding_amount

    # ================= Stock Health =================
    stock_health = frappe.db.sql("""
        SELECT item_code, MAX(modified) as last_move, SUM(actual_qty) as qty
        FROM `tabBin`
        GROUP BY item_code
    """, as_dict=True)

    dead = 0
    fast = 0

    for s in stock_health:
        days = date_diff(nowdate(), s.last_move)

        if days > 180:
            dead += s.qty
        elif days < 30:
            fast += s.qty

    return {
        "kpi": {
            "sales": sales,
            "purchase": purchase,
            "profit": profit,
            "margin": margin
        },
        "pending": {"labels": pending_labels, "values": pending_values},
        "stock": {"labels": stock_labels, "values": stock_values},
        "pie": {"top": top, "bottom": bottom},
        "trend": {"labels": trend_labels, "values": trend_values},
        "customer": {"labels": cust_labels, "values": cust_values},
        "profitability": {"labels": item_labels, "values": item_values},
        "aging": buckets,
        "stock_health": {"dead": dead, "fast": fast}
    }
