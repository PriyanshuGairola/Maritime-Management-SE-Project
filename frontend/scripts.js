// For Ship Owner Dashboard
if (document.getElementById('add-ship-form')) {
    document.getElementById('add-ship-form').addEventListener('submit', (event) => {
        event.preventDefault();

        const ship = {
            name: document.getElementById('name').value,
            type: document.getElementById('type').value,
            flag: document.getElementById('flag').value,
            imo: document.getElementById('imo').value,
            gross_tonnage: document.getElementById('gross-tonnage').value,
            net_tonnage: document.getElementById('net-tonnage').value,
            quality: document.getElementById('quality').value,
            age: document.getElementById('age').value,
            dom: document.getElementById('dom').value
        };

        fetch('/api/ships', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ship)
        })
        .then(response => response.json())
        .then(data => {
            alert('Ship added successfully');
            loadShips(); // Refresh the ship list
        })
        .catch(error => console.error('Error adding ship:', error));
    });
}

function loadShips() {
    fetch('/api/ships')
        .then(response => response.json())
        .then(data => {
            const shipList = document.getElementById('ship-list');
            shipList.innerHTML = '';
            data.forEach(ship => {
                const listItem = document.createElement('li');
                listItem.textContent = `Name: ${ship.name}, Type: ${ship.type}, Flag: ${ship.flag}`;
                shipList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching ships:', error));
}

// For Crew Member Dashboard
if (document.getElementById('show-readiness-form')) {
    document.getElementById('show-readiness-form').addEventListener('submit', (event) => {
        event.preventDefault();

        const date = document.getElementById('readiness-date').value;

        fetch('/api/readiness', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ date })
        })
        .then(response => response.json())
        .then(data => {
            const availableShipsList = document.getElementById('available-ships-list');
            availableShipsList.innerHTML = '';
            data.forEach(ship => {
                const listItem = document.createElement('li');
                listItem.textContent = `Name: ${ship.name}, Type: ${ship.type}, ETA: ${ship.eta}`;
                availableShipsList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching available ships:', error));
    });
}
// For Management Employee Dashboard (continued)
if (document.getElementById('add-ship-form-me')) {
    document.getElementById('add-ship-form-me').addEventListener('submit', (event) => {
        event.preventDefault();

        const ship = {
            name: document.getElementById('name-me').value,
            type: document.getElementById('type-me').value,
            flag: document.getElementById('flag-me').value,
            imo: document.getElementById('imo-me').value,
            gross_tonnage: document.getElementById('gross-tonnage-me').value,
            net_tonnage: document.getElementById('net-tonnage-me').value,
            quality: document.getElementById('quality-me').value,
            age: document.getElementById('age-me').value,
            dom: document.getElementById('dom-me').value
        };

        fetch('/api/ships', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ship)
        })
        .then(response => response.json())
        .then(data => {
            alert('Ship added successfully');
            loadFleet(); // Refresh the fleet ship list
        })
        .catch(error => console.error('Error adding ship:', error));
    });
}

function loadFleet() {
    fetch('/api/fleet')
        .then(response => response.json())
        .then(data => {
            const fleetShipList = document.getElementById('fleet-ship-list');
            fleetShipList.innerHTML = '';
            data.forEach(ship => {
                const listItem = document.createElement('li');
                listItem.textContent = `Name: ${ship.name}, Type: ${ship.type}, Flag: ${ship.flag}`;
                fleetShipList.appendChild(listItem);
            });
        })
        .catch(error => console.error('Error fetching fleet ships:', error));
}

// For Ship Dashboard
if (document.getElementById('update-status-form')) {
    document.getElementById('update-status-form').addEventListener('submit', (event) => {
        event.preventDefault();

        const statusUpdate = {
            status: document.getElementById('status').value,
            area: document.getElementById('area').value,
            destination: document.getElementById('destination').value,
            eta: document.getElementById('eta').value
        };

        fetch('/api/ship/status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(statusUpdate)
        })
        .then(response => response.json())
        .then(data => {
            alert('Status updated successfully');
            displayCurrentStatus(); // Refresh the current status
        })
        .catch(error => console.error('Error updating status:', error));
    });
}

function displayCurrentStatus() {
    fetch('/api/ship/status')
        .then(response => response.json())
        .then(data => {
            const currentStatus = document.getElementById('current-status');
            currentStatus.innerHTML = `
                Status: ${data.status}<br>
                Area: ${data.area}<br>
                Destination: ${data.destination}<br>
                ETA: ${data.eta}
            `;
        })
        .catch(error => console.error('Error fetching current status:', error));
}
