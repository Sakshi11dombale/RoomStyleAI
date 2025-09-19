// DOM elements
const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("file-upload");
const previewContainer = document.getElementById("preview-container");
const preview = document.getElementById("preview");
const analyzeBtn = document.querySelector(".analyze-btn");
const resultContainer = document.getElementById("result-container");

// Click to upload
dropArea.addEventListener("click", () => fileInput.click());

// Drag and drop events
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.style.background = "#fff0eb";
});

dropArea.addEventListener("dragleave", () => {
    dropArea.style.background = "transparent";
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.style.background = "transparent";
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        showPreview(files[0]);
    }
});

// Show preview ONLY
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        showPreview(fileInput.files[0]);
    }
});

function showPreview(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        preview.src = e.target.result;
        previewContainer.style.display = "block";
        dropArea.style.display = "none";
    };
    reader.readAsDataURL(file);
}

// Analyze button → send image to backend
analyzeBtn.addEventListener("click", async () => {
    if (!fileInput.files.length) {
        alert("Please upload a photo first!");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    resultContainer.innerHTML = "<p>Analyzing your room... ⏳</p>";

    try {
        const response = await fetch("http://127.0.0.1:8080/analyze", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        if (data.error) {
            resultContainer.innerHTML = `<p style="color:red;">${data.error}</p>`;
        } else {
            resultContainer.innerHTML = `
                <h3>AI Recommendations</h3>
                ${data.recommendations.map(r => `
                    <p><b>${r.style}</b> (${r.match}) - ${r.description}</p>
                `).join("")}

                <h4>Dominant Colors</h4>
                <div style="display:flex; gap:5px; justify-content:center;">
                    ${data.dominant_colors.map(c => `
                        <div style="width:30px; height:30px; background:rgb(${c[0]},${c[1]},${c[2]}); border-radius:5px;"></div>
                    `).join("")}
                </div>
            `;
        }
    } catch (err) {
        console.error("Error:", err);
        resultContainer.innerHTML = "<p style='color:red;'>Failed to analyze room. Please try again.</p>";
    }
});


