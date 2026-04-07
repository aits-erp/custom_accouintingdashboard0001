frappe.pages['accounting-dashboard'].on_page_load = function(wrapper) {

    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Accounting Dashboard',
        single_column: true
    });

    page.add_field({
        label: "Company",
        fieldname: "company",
        fieldtype: "Link",
        options: "Company"
    });

    page.set_primary_action("Refresh", () => load_dashboard(page));

    const html = $(`
        <div class="dashboard">

            <h3>Sales</h3>
            <div class="chart-row">
                <div id="sales_month"></div>
                <div id="sales_quarter"></div>
                <div id="sales_year"></div>
            </div>

            <h3>Purchase</h3>
            <div class="chart-row">
                <div id="pur_month"></div>
                <div id="pur_quarter"></div>
                <div id="pur_year"></div>
            </div>

            <h3>Pending Sales Orders</h3>
            <div id="pending_chart"></div>

            <h3>Stock Overview</h3>
            <div id="stock_chart"></div>

        </div>
    `);

    page.main.addClass("container-fluid");
    page.main.append(html);

    load_dashboard(page);
};


function load_dashboard(page) {

    let f = page.fields_dict;

    frappe.call({
        method: "accounting_dashboard.accounting_dashboard.page.accounting_dashboard.accounting_dashboard.get_dashboard_data",
        args: {
            company: f.company.get_value()
        },
        callback: function(r) {

            let d = r.message;

            draw_pie("sales_month", d.sales_month, "Sales Invoice");
            draw_pie("sales_quarter", d.sales_quarter, "Sales Invoice");
            draw_pie("sales_year", d.sales_year, "Sales Invoice");

            draw_pie("pur_month", d.pur_month, "Purchase Invoice");
            draw_pie("pur_quarter", d.pur_quarter, "Purchase Invoice");
            draw_pie("pur_year", d.pur_year, "Purchase Invoice");

            draw_bar("pending_chart", d.pending);
            draw_bar("stock_chart", d.stock);
        }
    });
}


function draw_pie(id, data, doctype) {

    let chart = new frappe.Chart(`#${id}`, {
        data: { labels: data.labels, datasets: [{ values: data.values }] },
        type: "pie",
        height: 220
    });

    chart.parent.addEventListener("click", () => {
        frappe.set_route("List", doctype);
    });
}


function draw_bar(id, data) {

    new frappe.Chart(`#${id}`, {
        data: { labels: data.labels, datasets: [{ values: data.values }] },
        type: "bar",
        height: 300
    });
}
