frappe.pages['accounting-dashboard'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Accounting Dashboard',
        single_column: true
    });

    page.add_field({ label: "From Date", fieldname: "from_date", fieldtype: "Date" });
    page.add_field({ label: "To Date", fieldname: "to_date", fieldtype: "Date" });
    page.add_field({ label: "Company", fieldname: "company", fieldtype: "Link", options: "Company" });

    page.set_primary_action("Refresh", () => load_dashboard());
    page.add_action_item("Export Excel", () => frappe.msgprint("Excel export coming soon"));

    $(wrapper).find('.layout-main-section').html(`
        <div class="dashboard-grid">

            <div id="kpi"></div>

            <div class="chart-box"><h4>Pending Sales</h4><div id="pending_chart"></div></div>

            <div class="chart-box"><h4>Stock</h4><div id="stock_chart"></div></div>

            <div class="chart-box"><h4>Top vs Bottom Stock</h4><div id="pie_chart"></div></div>

            <div class="chart-box"><h4>Sales Trend</h4><div id="trend_chart"></div></div>

            <div class="chart-box"><h4>Customer Contribution</h4><div id="customer_chart"></div></div>

            <div class="chart-box"><h4>Product Profitability</h4><div id="profit_chart"></div></div>

            <div class="chart-box"><h4>Aging Dashboard</h4><div id="aging_chart"></div></div>

            <div class="chart-box"><h4>Stock Health</h4><div id="health_chart"></div></div>

        </div>
    `);

    load_dashboard();
    setInterval(load_dashboard, 60000);
};


function load_dashboard() {

    let filters = frappe.pages['accounting-dashboard'].page.fields_dict;

    frappe.call({
        method: "accounting_dashboard.accounting_dashboard.page.accounting_dashboard.accounting_dashboard.get_dashboard_data",
        args: {
            from_date: filters.from_date.get_value(),
            to_date: filters.to_date.get_value(),
            company: filters.company.get_value()
        },
        callback: function(r) {

            let d = r.message;

            render_kpi(d.kpi);

            render_chart("#pending_chart", d.pending, "bar", true);
            render_chart("#stock_chart", d.stock, "bar", true);
            render_pie(d.pie);
            render_chart("#trend_chart", d.trend, "line");

            render_customer(d.customer);
            render_profit(d.profitability);
            render_aging(d.aging);
            render_health(d.stock_health);
        }
    });
}


// ================= KPI =================
function render_kpi(kpi) {

    $("#kpi").html(`
        <div class="kpi-grid">
            <div class="kpi">Sales<br>₹${kpi.sales.toLocaleString()}</div>
            <div class="kpi">Purchase<br>₹${kpi.purchase.toLocaleString()}</div>
            <div class="kpi profit">Profit<br>₹${kpi.profit.toLocaleString()}</div>
            <div class="kpi">Margin<br>${kpi.margin.toFixed(2)}%</div>
        </div>
    `);
}


// ================= Generic Chart =================
function render_chart(id, data, type, drill=false) {

    let chart = new frappe.Chart(id, {
        data: { labels: data.labels, datasets: [{ values: data.values }] },
        type: type,
        height: 300,
        animate: 1
    });

    if (drill) {
        chart.parent.addEventListener("click", () => {
            frappe.set_route("query-report", "Stock Balance");
        });
    }
}


// ================= Pie Top/Bottom =================
function render_pie(data) {

    new frappe.Chart("#pie_chart", {
        data: {
            labels: ["Top 100", "Bottom 100"],
            datasets: [{ values: [data.top, data.bottom] }]
        },
        type: "pie",
        height: 300,
        animate: 1
    });
}


// ================= Customer Pie =================
function render_customer(data) {

    new frappe.Chart("#customer_chart", {
        data: { labels: data.labels, datasets: [{ values: data.values }] },
        type: "pie",
        height: 300,
        animate: 1
    });
}


// ================= Profitability =================
function render_profit(data) {

    new frappe.Chart("#profit_chart", {
        data: { labels: data.labels, datasets: [{ values: data.values }] },
        type: "bar",
        height: 300,
        animate: 1
    });
}


// ================= Aging =================
function render_aging(data) {

    new frappe.Chart("#aging_chart", {
        data: {
            labels: Object.keys(data),
            datasets: [{ values: Object.values(data) }]
        },
        type: "bar",
        height: 300,
        animate: 1
    });
}


// ================= Stock Health =================
function render_health(data) {

    new frappe.Chart("#health_chart", {
        data: {
            labels: ["Fast Moving", "Dead Stock"],
            datasets: [{ values: [data.fast, data.dead] }]
        },
        type: "pie",
        height: 300,
        animate: 1
    });
}
