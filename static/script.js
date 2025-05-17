document.getElementById('prediction-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const button = this.querySelector('button');
    button.disabled = true;
    button.textContent = 'Predicting...';
    
    const formData = new FormData(this);
    
    fetch('/predict', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const resultDiv = document.getElementById('result');
        if (data.error) {
            resultDiv.innerHTML = `Error: ${data.error}`;
            resultDiv.className = 'red';
        } else {
            resultDiv.innerHTML = `Predicted Cancer Stage: ${data.prediction}`;
            resultDiv.className = 'green';
        }
    })
    .catch(error => {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `Error: ${error.message}`;
        resultDiv.className = 'red';
    })
    .finally(() => {
        button.disabled = false;
        button.textContent = 'Predict';
    });
});