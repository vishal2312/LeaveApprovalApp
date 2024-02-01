function applyFilters() {
    const emailFilter = document.getElementById("email").value;
    const fetchURL = `/admin_dashboard?email=${emailFilter}`;

    fetch(API_URL + fetchURL, {
        method: "GET",
        credentials: "include",
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then((response) => {
        if (response.ok) {
            return response.json();
        }
        return Promise.reject(response);
    })
    .then((data) => {
        updateTable(data.items);
        updateDashboard(data);
    });
}

function updateTable(items) {
    console.log("Table data received:", items);

    const tbody = document.querySelector(".leaveTableBody");
    tbody.innerHTML = ""; // Clear existing rows

    items.forEach(item => {
        console.log("Processing item:", item);

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.applied_on}</td>
            <td>${item.name}</td>
            <td>${item.email}</td>
            <td>${item.leave_type}</td>
            <td>${item.from_date}</td>
            <td>${item.to_date}</td>
            <td>${item.no_of_days}</td>
            <td>${item.reason}</td>
            <td>${item.status}</td>
        `;
        tbody.appendChild(row);
    });
}

function updateDashboard(data) {
    console.log("Dashboard data received:", data);

    // Access additional data
    const totalLeaves = data.total_leaves;
    const totalPlanned = data.total_planned;
    const totalUnplanned = data.total_unplanned;
    const totalLwp = data.total_lwp

    // Update your dashboard elements with the additional data
    document.getElementById("totalLeaves").textContent = `${data.total_leaves_taken} / ${data.total_leaves}`;
    document.getElementById("totalPlanned").textContent = `${data.total_planned_taken} / ${data.total_planned}`;
    document.getElementById("totalUnplanned").textContent = `${data.total_unplanned_taken} / ${data.total_unplanned}`;
    document.getElementById("totalLwp").textContent = `${data.total_lwp}`;
}
