document.addEventListener('DOMContentLoaded', function () {
    flatpickr('#dateFilter', {
        mode: 'range',
        dateFormat: 'm/d/20y',
        onClose: applyFilters
    });
    applyFilters();

    document.getElementById('nameFilter').addEventListener('input', toggleClearNameButton);
    document.getElementById('dateFilter').addEventListener('input', toggleClearDateButton);

    document.getElementById('clearNameButton').addEventListener('click', clearNameAndHideButton);
    document.getElementById('clearDateButton').addEventListener('click', clearDateAndHideButton);
});

const itemsPerPage = 10; 
let currentPage = 1;
let currentItems;

function applyFilters() {
    const statusFilter = document.getElementById("statusFilter").value;
    const nameFilter = document.getElementById("nameFilter").value.toLowerCase();
    const dateRangeFilter = document.getElementById("dateFilter").value;

    const fetchURL = `/manage_leave?status=${statusFilter}&name=${nameFilter}&date_range=${dateRangeFilter}`;
    showLoader();
    fetch(API_URL + fetchURL, {
        method: "GET",
        credentials: "include",
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then((response) => response.ok ? response.json() : Promise.reject(response))
        .then((data) => {
            hideLoader();
            currentItems = data;
            updateTable(currentItems); 
        });
}

function updateTable(items) {
    const tbody = document.getElementById("leaveTableBody");
    tbody.innerHTML = "";

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedItems = items.slice(startIndex, endIndex);

    paginatedItems.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.applied_on}</td>
            <td>${item.name}</td>
            <td>${item.email}</td>
            <td><span id="leaveType_${item.id}">${item.leave_type}</span></td>
            <td>${item.from_date}</td>
            <td>${item.to_date}</td>
            <td>${item.no_of_days}</td>
            <td class="reason-cell">${item.reason}</td>
            
            <td>
                ${item.status === 'Pending' ? 
                    `<button id="approveBtn" onclick="approveLeave('${item.id}')">Approve</button>
                    <button id="rejectBtn" onclick="rejectLeave('${item.id}')">Reject</button>` :
                    item.status
                }
            </td>

            <td>
                <button id="editStatusBtn" onclick="editStatus('${item.id}', '${item.leave_type}')">Edit</button>
                <button id="saveStatusBtn" onclick="saveStatus('${item.id}')">Save</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    updatePaginationControls(items.length);
}

function updatePaginationControls(totalItems) { 
    const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
    currentPage = Math.min(Math.max(1, currentPage), totalPages);

    const currentPageElement = document.getElementById("currentPage");
    currentPageElement.textContent = `Page ${currentPage} of ${totalPages}`;

    const prevPageButton = document.getElementById("prevPage");
    const nextPageButton = document.getElementById("nextPage");

    prevPageButton.disabled = currentPage === 1;
    nextPageButton.disabled = currentPage === totalPages;

    prevPageButton.removeEventListener("click", goToPreviousPage);
    nextPageButton.removeEventListener("click", goToNextPage);

    if (currentPage !== 1) {
        prevPageButton.addEventListener("click", goToPreviousPage);
    }

    if (currentPage !== totalPages) {
        nextPageButton.addEventListener("click", goToNextPage);
    }
}

function goToPreviousPage() {
    changePage(currentPage - 1);
}

function goToNextPage() {
    changePage(currentPage + 1);
}

async function changePage(newPage) {
    currentPage = newPage;
    await applyFilters();
}

function approveLeave(leaveId) { 
    updateLeaveStatus(leaveId, 'Approved');
}

function rejectLeave(leaveId) {
    updateLeaveStatus(leaveId, 'Rejected');
}

function updateLeaveStatus(leaveId, newStatus) {
    showLoader();
    fetch(`/manage_leave/${leaveId}/${newStatus}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            applyFilters(); 
            hideLoader();
        })
        .catch(error => console.error('Error:', error));
}

function clearDateFilter() {
    document.getElementById('dateFilter').value = '';
    applyFilters();
    hideClearDateButton();
}

function clearNameFilter() {
    document.getElementById('nameFilter').value = '';
    applyFilters();
    hideClearNameButton();
}

function showLoader() {
    document.getElementById('loaderOverlay').style.display = 'flex';
}

function hideLoader() {
    document.getElementById('loaderOverlay').style.display = 'none';
}

function editStatus(leaveId, currentLeaveType) {
    const leaveTypeElement = document.getElementById(`leaveType_${leaveId}`);
    const selectElement = document.createElement("select");
    selectElement.setAttribute("id", `editLeaveType_${leaveId}`);
    const leaveTypeOptions = ["", "Planned", "Unplanned", "LWP"];
    leaveTypeOptions.forEach(optionValue => {
        const optionElement = document.createElement("option");
        optionElement.setAttribute("value", optionValue);
        optionElement.textContent = optionValue;
        selectElement.appendChild(optionElement);
    });
    selectElement.value = currentLeaveType;
    leaveTypeElement.innerHTML = "";
    leaveTypeElement.appendChild(selectElement);
}

function saveStatus(leaveId) {
    const selectElement = document.getElementById(`editLeaveType_${leaveId}`);
    const newLeaveType = selectElement.value;
    showLoader();
    fetch(`/manage_leave/${leaveId}?leave_type=${encodeURIComponent(newLeaveType)}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ leave_type: newLeaveType }),
    })
    .then(response => response.ok ? response.json() : Promise.reject('Failed to save leave type'))
    .then(data => {
        applyFilters(); 
        hideLoader();
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoader();
    });
}

function toggleClearNameButton() {
    const clearNameButton = document.getElementById('clearNameButton');
    clearNameButton.style.display = document.getElementById('nameFilter').value.trim() !== '' ? 'inline-block' : 'none';
}

function toggleClearDateButton() {
    const clearDateButton = document.getElementById('clearDateButton');
    clearDateButton.style.display = document.getElementById('dateFilter').value.trim() !== '' ? 'inline-block' : 'none';
}

function hideClearNameButton() {
    const clearNameButton = document.getElementById('clearNameButton');
    clearNameButton.style.display = 'none';
}

function hideClearDateButton() {
    const clearDateButton = document.getElementById('clearDateButton');
    clearDateButton.style.display = 'none';
}


function downloadExcel() {
    const items = currentItems; 
    const columnsToExport = ['applied_on', 'name', 'email', 'leave_type', 'from_date', 'to_date', 'no_of_days', 'reason', 'status'];

    const filteredItems = items.map(item => {
        const filteredItem = {};
        columnsToExport.forEach(column => {
            filteredItem[column] = item[column];
        });
        return filteredItem;
    });

    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.json_to_sheet(filteredItems);
    XLSX.utils.book_append_sheet(workbook, worksheet, 'LeavesData');
    XLSX.writeFile(workbook, 'LeavesData.xlsx', { bookType: 'xlsx', mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
}
