
const fileInput = document.getElementById('currencyImage');
const submitBtn = document.getElementById('submitBtn');
const resultDiv = document.getElementById('result');
const uploadedImage = document.getElementById('uploadedImage');

// Hide result and image preview initially
resultDiv.classList.add('hidden');
uploadedImage.classList.add('hidden');

// Event listener for file input
fileInput.addEventListener('change', function () {
    const fileLabel = document.getElementById('fileLabel');
    if (this.files && this.files[0]) {
        // Update file label text
        fileLabel.innerHTML = "<i class='fas fa-upload'></i> Image uploaded";

        // Display the uploaded image
        const reader = new FileReader();
        reader.onload = function (e) {
            uploadedImage.src = e.target.result;
            uploadedImage.classList.remove('hidden');
        };
        reader.readAsDataURL(this.files[0]);
    }
});

// Event listener for the submit button
submitBtn.addEventListener('click', async function () {
    if (fileInput.files.length === 0) {
        resultDiv.innerHTML = "Please upload an image.";
        resultDiv.classList.remove("hidden");
        resultDiv.style.color = "red";
    } else {
        resultDiv.innerHTML = "Processing... Please wait.";
        resultDiv.classList.remove("hidden");
        resultDiv.style.color = "green";

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8001/predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                resultDiv.innerHTML = `Prediction: ${data.class}<br>Confidence: ${data.confidence.toFixed(2)}%`;
                resultDiv.style.color = data.class === "realNotes" ? "green" : "red";
            } else {
                resultDiv.innerHTML = `Error: ${data.error}`;
                resultDiv.style.color = "red";
            }
        } catch (error) {
            resultDiv.innerHTML = `An error occurred: ${error.message}`;
            resultDiv.style.color = "red";
        }
    }
});
