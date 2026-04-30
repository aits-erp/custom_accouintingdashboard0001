# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": _("Sr. No."), "fieldname": "sr_no", "fieldtype": "Data", "width": 80},
        {"label": _("DETAILS OF ACTIVITY"), "fieldname": "details_of_activity", "fieldtype": "Text", "width": 250},
        {"label": _("QUOTE REF IF ANY"), "fieldname": "quote_ref", "fieldtype": "Data", "width": 150},
        {"label": _("COMPANY NAME"), "fieldname": "company_name", "fieldtype": "Data", "width": 200},
        {"label": _("PERSON CONTACTED"), "fieldname": "person_contacted", "fieldtype": "Data", "width": 180},
        {"label": _("PHONE NUMBER"), "fieldname": "phone_number", "fieldtype": "Data", "width": 130},
        {"label": _("DETAILED OUTCOME OF ACTIVITY"), "fieldname": "detailed_outcome", "fieldtype": "Text", "width": 300},
        {"label": _("Pyro Clark reliance"), "fieldname": "pyro_clark_reliance", "fieldtype": "Data", "width": 150},
        {"label": _("NEXT ACTION TO BE DONE"), "fieldname": "next_action", "fieldtype": "Text", "width": 200},
        {"label": _("FOLLOW UP-1 UPDATE"), "fieldname": "follow_up_1_update", "fieldtype": "Text", "width": 200},
        {"label": _("DATE"), "fieldname": "follow_up_1_date", "fieldtype": "Date", "width": 100},
        {"label": _("FOLLOW UP-2 UPDATE"), "fieldname": "follow_up_2_update", "fieldtype": "Text", "width": 200},
        {"label": _("DATE"), "fieldname": "follow_up_2_date", "fieldtype": "Date", "width": 100}
    ]

def get_data(filters):
    conditions = "1=1"
    values = []
    
    # Apply filters
    if filters and filters.get("from_date"):
        conditions += " AND l.modified >= %s"
        values.append(filters.get('from_date'))
    if filters and filters.get("to_date"):
        conditions += " AND l.modified <= %s"
        values.append(filters.get('to_date'))
    if filters and filters.get("company_name"):
        conditions += " AND l.company_name LIKE %s"
        values.append(f'%%{filters.get("company_name")}%%')
    
    query = f"""
        SELECT 
            l.name as lead_name,
            l.modified as date,
            l.company_name,
            l.first_name,
            l.last_name,
            l.mobile_no,
            l.phone,
            l.custom_details_of_activity as details_of_activity,
            l.custom_detailed_outcome as detailed_outcome,
            
            /* Get Quotation reference from Quotation doctype linked to this lead */
            (SELECT GROUP_CONCAT(name SEPARATOR ', ') 
             FROM `tabQuotation` 
             WHERE party_name = l.name AND docstatus = 1) as quote_ref,
            
            /* Get data from Opportunity linked to this Lead */
            o.name as opportunity_name,
            o.custom_pyro_clark_reliance as pyro_clark_reliance,
            o.custom_next_action_to_be_done as next_action,
            o.custom_follow_up1_update as follow_up_1_update,
            o.custom_follow_up1_date as follow_up_1_date,
            o.custom_follow_up2_update as follow_up_2_update,
            o.custom_follow_up2_date as follow_up_2_date
            
        FROM `tabLead` l
        
        /* Left join with Opportunity */
        LEFT JOIN `tabOpportunity` o ON o.party_name = l.name AND o.party_type = 'Lead'
        
        WHERE {conditions}
        ORDER BY l.modified DESC
    """
    
    data = frappe.db.sql(query, values, as_dict=1)
    
    # Process the data and add serial numbers
    for idx, row in enumerate(data, start=1):
        row["sr_no"] = idx
        
        # Combine first_name and last_name for person contacted
        person_name = []
        if row.get("first_name"):
            person_name.append(row.get("first_name"))
        if row.get("last_name"):
            person_name.append(row.get("last_name"))
        row["person_contacted"] = " ".join(person_name) if person_name else ""
        
        # Combine phone numbers
        phone_numbers = []
        if row.get("mobile_no"):
            phone_numbers.append(row.get("mobile_no"))
        if row.get("phone"):
            phone_numbers.append(row.get("phone"))
        row["phone_number"] = ", ".join(phone_numbers) if phone_numbers else ""
        
        # Handle None values
        row["details_of_activity"] = row.get("details_of_activity") or ""
        row["detailed_outcome"] = row.get("detailed_outcome") or ""
        row["quote_ref"] = row.get("quote_ref") or ""
        row["pyro_clark_reliance"] = row.get("pyro_clark_reliance") or ""
        row["next_action"] = row.get("next_action") or ""
        row["follow_up_1_update"] = row.get("follow_up_1_update") or ""
        row["follow_up_2_update"] = row.get("follow_up_2_update") or ""
    
    return data