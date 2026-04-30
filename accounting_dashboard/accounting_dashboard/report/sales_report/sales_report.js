// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt


frappe.query_reports["Sales Reporting"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "width": 100
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": 100
        },
        {
            "fieldname": "company_name",
            "label": __("Company Name"),
            "fieldtype": "Data",
            "width": 150
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Highlight missing next actions
        if (column.fieldname === "next_action" && (!value || value === "None" || value === "")) {
            value = '<span style="color: red; font-weight: bold;">⚠️ No Next Action</span>';
        }
        
        // Highlight pending follow-ups
        if (column.fieldname === "follow_up_1_update" && (!value || value === "None" || value === "")) {
            value = '<span style="color: orange;">⏳ Pending</span>';
        }
        
        if (column.fieldname === "follow_up_2_update" && (!value || value === "None" || value === "")) {
            value = '<span style="color: orange;">⏳ Pending</span>';
        }
        
        // Color code quote references
        if (column.fieldname === "quote_ref" && value && value !== "None" && value !== "") {
            value = '<span style="color: green; font-weight: bold;">📄 ' + value + '</span>';
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add export button
        report.page.add_inner_button(__("Export to Excel"), function() {
            frappe.call({
                method: "frappe.client.export_query",
                args: {
                    doctype: "Lead",
                    report_name: "Lead Activity Report",
                    file_format: "Excel"
                }
            });
        });
        
        // Add refresh button
        report.page.add_inner_button(__("Refresh"), function() {
            report.refresh();
        });
    }
};