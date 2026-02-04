frappe.query_reports["Custom Items"] = {
    tree: true,
    initial_depth: 3,

    filters: [
        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Warehouse"
        },
        {
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group"
        }
    ]
};
