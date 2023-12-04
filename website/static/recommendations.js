function filterResults(filterType) {
    let sortedData;
    switch (filterType) {
        case 'rating':
            sortedData = recommendations.slice().sort((a, b) => (a.rating > b.rating) ? -1 : 1);
            break;
        case 'name':
            sortedData = recommendations.slice().sort((a, b) => a.name.localeCompare(b.name));
            break;
        default:
            sortedData = recommendations;
    }

    displayResults(sortedData);
}

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = ''; // clear previous results
    if (data.length === 0) {
        window.location.href = 'recommendation'; // Redirect if there are no cards
        alert("No results found. Please try again.");
        return;
    }
    data.forEach(rec => {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-md-4 mb-4';

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';
        
        // Add click event listener to each card
        cardDiv.addEventListener('click', () => {
            handleCardClick(rec.name, rec.address); // pass data on click
        });

        cardDiv.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${rec.name}</h5>
                <p class="card-text">Rating: ${rec.rating} &#9733;<br> Address: ${rec.address}</p>
            </div>
        `;
        cardDiv.classList.add('clickable-card');

        colDiv.appendChild(cardDiv);
        resultsDiv.appendChild(colDiv);
    });
}

function handleCardClick(cardName, cardAddress) {
    fetch('/results', {
        method: 'POST',
        body: JSON.stringify({ cardName, cardAddress }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; // redirect if Flask sends redirect
        } else {
            console.log('No redirect response');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function showInitialResults() {
    displayResults(recommendations);
}
showInitialResults();
