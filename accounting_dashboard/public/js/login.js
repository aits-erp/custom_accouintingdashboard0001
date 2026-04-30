frappe.router.on('change', () => {

    // Prevent duplicate button
    if (document.getElementById("dashboard-circle-btn")) return;

    setTimeout(() => {

        let btn = document.createElement("div");
        btn.id = "dashboard-circle-btn";
        btn.innerText = "D";

        // Style (circular button)
        btn.style.position = "fixed";
        btn.style.top = "80px";   // below blue navbar
        btn.style.right = "20px";
        btn.style.width = "50px";
        btn.style.height = "50px";
        btn.style.borderRadius = "50%";
        btn.style.backgroundColor = "#5e64ff";
        btn.style.color = "#fff";
        btn.style.display = "flex";
        btn.style.alignItems = "center";
        btn.style.justifyContent = "center";
        btn.style.fontSize = "20px";
        btn.style.fontWeight = "bold";
        btn.style.cursor = "pointer";
        btn.style.zIndex = "9999";
        btn.style.boxShadow = "0 4px 10px rgba(0,0,0,0.2)";

        // Hover effect
        btn.onmouseenter = () => {
            btn.style.backgroundColor = "#4b50e6";
        };
        btn.onmouseleave = () => {
            btn.style.backgroundColor = "#5e64ff";
        };

        // Click action
        btn.onclick = () => {
            frappe.set_route("dashboard-view", "Home");
        };

        document.body.appendChild(btn);

        console.log("✅ Circular Dashboard Button Added");

    }, 1000);
});