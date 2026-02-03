import frappe


def format_rows(rows):
    if not rows:
        return {"labels": ["No Data"], "values": [0]}
    return {
        "labels": [r[0] for r in rows],
        "values": [float(r[1]) for r in rows]
    }


@frappe.whitelist()
def get_dashboard_data(company=None):

    cfilter = f" AND company='{company}'" if company else ""

    # ---------- SALES ----------
    sales_month = frappe.db.sql(f"""
        SELECT MONTHNAME(posting_date), SUM(grand_total)
        FROM `tabSales Invoice`
        WHERE docstatus=1 {cfilter}
        GROUP BY MONTH(posting_date)
    """)

    sales_quarter = frappe.db.sql(f"""
        SELECT CONCAT('Q',QUARTER(posting_date)), SUM(grand_total)
        FROM `tabSales Invoice`
        WHERE docstatus=1 {cfilter}
        GROUP BY QUARTER(posting_date)
    """)

    sales_year = frappe.db.sql(f"""
        SELECT YEAR(posting_date), SUM(grand_total)
        FROM `tabSales Invoice`
        WHERE docstatus=1 {cfilter}
        GROUP BY YEAR(posting_date)
    """)

    # ---------- PURCHASE ----------
    pur_month = frappe.db.sql(f"""
        SELECT MONTHNAME(posting_date), SUM(grand_total)
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 {cfilter}
        GROUP BY MONTH(posting_date)
    """)

    pur_quarter = frappe.db.sql(f"""
        SELECT CONCAT('Q',QUARTER(posting_date)), SUM(grand_total)
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 {cfilter}
        GROUP BY QUARTER(posting_date)
    """)

    pur_year = frappe.db.sql(f"""
        SELECT YEAR(posting_date), SUM(grand_total)
        FROM `tabPurchase Invoice`
        WHERE docstatus=1 {cfilter}
        GROUP BY YEAR(posting_date)
    """)

    # ---------- BAR DASHBOARD ----------
    pending = frappe.db.sql("""
        SELECT customer, SUM(grand_total)
        FROM `tabSales Order`
        WHERE docstatus=1 AND per_delivered < 100
        GROUP BY customer
        LIMIT 10
    """)

    stock = frappe.db.sql("""
        SELECT item_code, SUM(actual_qty)
        FROM `tabBin`
        GROUP BY item_code
        LIMIT 10
    """)

    return {
        "sales_month": format_rows(sales_month),
        "sales_quarter": format_rows(sales_quarter),
        "sales_year": format_rows(sales_year),
        "pur_month": format_rows(pur_month),
        "pur_quarter": format_rows(pur_quarter),
        "pur_year": format_rows(pur_year),
        "pending": format_rows(pending),
        "stock": format_rows(stock)
    }
