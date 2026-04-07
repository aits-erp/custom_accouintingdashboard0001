frappe.router.on('change', () => {

    // Avoid duplicate button
    if (document.getElementById("custom-dashboard-btn")) return;

    setTimeout(() => {

        let navbar = document.querySelector(".navbar .container");

        if (navbar) {
            let btn = document.createElement("button");
            btn.id = "custom-dashboard-btn";
            btn.innerText = "Dashboard";
            btn.className = "btn btn-primary";
            btn.style.marginLeft = "10px";

            btn.onclick = () => {
                frappe.set_route("dashboard-view", "Home");
            };

            navbar.appendChild(btn);

            console.log("✅ Dashboard button added");
        }

    }, 1000);
});

//changes