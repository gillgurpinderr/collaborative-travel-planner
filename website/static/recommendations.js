// Dummy data (Replace with real data from your backend)
const recommendations = [
    { name: "Restaurant A", nowOpen: true, fastResponding: true, price: "$$" },
    { name: "Restaurant B", nowOpen: false, fastResponding: true, price: "$" },
    // ... more data
];

// Function to filter and display results
function filterResults(filterType) {
    let filteredData;
    switch(filterType) {
        case 'nowOpen':
            filteredData = recommendations.filter(r => r.nowOpen);
            break;
        case 'fastResponding':
            filteredData = recommendations.filter(r => r.fastResponding);
            break;
        case 'price':
            filteredData = recommendations.sort((a, b) => a.price.length - b.price.length);
            break;
        default:
            filteredData = recommendations;
    }

    displayResults(filteredData);
}

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = ''; // Clear previous results
    data.forEach(rec => {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-md-4 mb-4';

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';

        cardDiv.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${rec.name}</h5>
                <p class="card-text">Now Open: ${rec.nowOpen ? 'Yes' : 'No'}, Fast Responding: ${rec.fastResponding ? 'Yes' : 'No'}, Price: ${rec.price}</p>
            </div>
        `;

        colDiv.appendChild(cardDiv);
        resultsDiv.appendChild(colDiv);
    });
}

// Initially display all results
displayResults(recommendations);
