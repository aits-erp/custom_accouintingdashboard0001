frappe.query_reports["Purchase Roll Report"] = {
    filters: [
        {
            fieldname: "item_code",
            label: "Item Code",
            fieldtype: "Link",
            options: "Item"
        },
        {
            fieldname: "roll_no",
            label: "Roll No",
            fieldtype: "Data"
        },
        {
            fieldname: "rack",
            label: "Rack",
            fieldtype: "Data"
        },
        {
            fieldname: "colour_code",
            label: "Colour Code",
            fieldtype: "Data"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (data && data.item_code === "GRAND TOTAL") {
            value = `<b style="color:green">${value}</b>`;
        }

        return value;
    }
};
