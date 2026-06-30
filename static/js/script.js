const textarea = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");
const chatBox = document.getElementById("chat-box");
const resultCount = document.getElementById("result-count");
const suggestedQuestions = [

    "How does ANN work?",

    "What are Activation Functions?",

    "Explain CNN in Deep Learning.",

    "What is Backpropagation?",

    "What is Gradient Descent?",

    "Explain Forward Propagation.",

    "What is Perceptron?",

    "What is Multi Layer Perceptron?",

    "Explain Vanishing Gradient.",

    "What is Binary Cross Entropy?"


];

let suggestionIndex = 0;

// ========================================
// Auto Resize Textarea
// ========================================

textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
});

// ========================================
// Send on Enter
// ========================================

textarea.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();
        askQuestion();

    }

});

sendBtn.addEventListener("click", askQuestion);

// ========================================
// Main Function
// ========================================

async function askQuestion() {

    const question = textarea.value.trim();

    if (!question) return;

    chatBox.innerHTML = "";

    resultCount.innerText = "Searching...";

    sendBtn.disabled = true;
    textarea.disabled = true;

    sendBtn.innerText = "Searching";

    showLoading();

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        if (!response.ok) {

            throw new Error("Server Error");

        }

        const data = await response.json();

        hideLoading();

        // Check if server returned an error
        if (data.error) {
            displayError(data.error);
        } else {
            displayCards(data.results);
        }

        textarea.value = "";
        textarea.style.height = "auto";

    }

    catch (error) {

        hideLoading();

        displayError(error.message);

    }

    finally {

        sendBtn.disabled = false;
        textarea.disabled = false;

        sendBtn.innerText = "Search";

    }

}

// ========================================
// Loading Animation
// ========================================

function showLoading() {

    chatBox.innerHTML = `

        <div class="loading">

            <span></span>
            <span></span>
            <span></span>

        </div>

    `;

}

// ========================================
// Hide Loading
// ========================================

function hideLoading() {

    chatBox.innerHTML = "";

}

// ========================================
// Display Answer
// ========================================

function displayCards(results) {

    if (!results || results.length === 0) {

        resultCount.innerText = "No Results";

        chatBox.innerHTML = `

        <div class="message">

            <div class="message-content">

                No relevant videos for this question.

            </div>

        </div>

        `;

        return;

    }

    resultCount.innerText = `${results.length} Relevant Results`;

    let html = "";

    results.forEach(video => {

        const timestampsHtml = video.timestamps.map(t => {

            const minutes = Math.floor(t.seconds / 60);
            const seconds = Math.floor(t.seconds % 60);

            return `

                <div class="timestamp-item">

                    <div class="time-pill">

                        ${minutes}:${String(seconds).padStart(2, "0")}

                    </div>

                    <div class="timestamp-description">

                        ${t.description}

                    </div>

                </div>

            `;

        }).join("");

        html += `

        <div class="video-card">

            <div class="video-number">

                VIDEO ${video.video_number}

            </div>

            <div class="video-title">

                ${video.video_title}

            </div>

            <div class="timestamps">

                ${timestampsHtml}

            </div>

            <div class="video-actions">

                <a
                    href="${video.youtube_url}"
                    target="_blank"
                    class="watch-btn"
                >

                    Continue Learning →

                </a>

            </div>

        </div>

        `;

    });

    chatBox.innerHTML = html;

}

// ========================================
// Display Error
// ========================================

function displayError(error) {

    resultCount.innerText = "Error";

    chatBox.innerHTML = `

        <div class="message">

            <div class="message-title">

                <h3>Something went wrong</h3>

            </div>

            <div class="message-content">

                ${escapeHtml(error)}

            </div>

            <div class="message-content" style="margin-top: 8px; font-size: 0.85em; opacity: 0.7;">

                Check the Vercel Function Logs for more details.

            </div>

        </div>

    `;

}

// ========================================
// Markdown Formatter
// ========================================

function formatMarkdown(text) {

    if (!text) return "";

    return escapeHtml(text)

        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")

        .replace(/\*(.*?)\*/g, "<em>$1</em>")

        .replace(/`(.*?)`/g, "<code>$1</code>")

        .replace(/\n/g, "<br>");

}

// ========================================
// Escape HTML
// ========================================

function escapeHtml(text) {

    return text

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}

const sidebar = document.getElementById("sidebar");

const main = document.getElementById("main-content");

const toggle = document.getElementById("sidebar-toggle");

const app = document.querySelector(".app");

toggle.addEventListener("click", () => {

    sidebar.classList.toggle("collapsed");

    document.querySelector(".main-content")
            .classList.toggle("expanded");

    app.classList.toggle("sidebar-collapsed");

});

const suggestionText = document.getElementById("suggested-question");

function rotateSuggestion(){

    suggestionIndex++;

    if(suggestionIndex >= suggestedQuestions.length){

        suggestionIndex = 0;

    }

    suggestionText.innerHTML =
        `Try: ${suggestedQuestions[suggestionIndex]}`;

}

setInterval(rotateSuggestion,5000);

const bottomBtn = document.getElementById("bottom-search-btn");

bottomBtn.addEventListener("click",()=>{

    textarea.value = suggestedQuestions[suggestionIndex];

    askQuestion();

});

// ========================================
// About Modal
// ========================================

const aboutBtn = document.getElementById("about-btn");
const aboutModal = document.getElementById("about-modal");
const closeAbout = document.getElementById("close-about");

if (aboutBtn && aboutModal && closeAbout) {

    aboutBtn.addEventListener("click", (e) => {

        e.preventDefault();

        aboutModal.classList.add("show");

        document.body.style.overflow = "hidden";

    });

    closeAbout.addEventListener("click", () => {

        aboutModal.classList.remove("show");

        document.body.style.overflow = "auto";

    });

    aboutModal.addEventListener("click", (e) => {

        if (e.target === aboutModal) {

            aboutModal.classList.remove("show");

            document.body.style.overflow = "auto";

        }

    });

    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {

            aboutModal.classList.remove("show");

            document.body.style.overflow = "auto";

        }

    });

}


// ========================================
// Mobile Sidebar Management
// ========================================

function isMobile() {
    return window.innerWidth <= 992;
}

// Backdrop element for mobile sidebar overlay
const sidebarBackdrop = document.createElement("div");
sidebarBackdrop.classList.add("sidebar-backdrop", "hidden");
document.body.appendChild(sidebarBackdrop);

function closeSidebarMobile() {
    if (!sidebar.classList.contains("collapsed")) {
        sidebar.classList.add("collapsed");
        main.classList.add("expanded");
        app.classList.add("sidebar-collapsed");
    }
    sidebarBackdrop.classList.add("hidden");
}

// Auto-collapse sidebar on mobile load
if (isMobile()) {
    closeSidebarMobile();
}

// Show/hide backdrop when toggle is clicked on mobile
toggle.addEventListener("click", () => {
    if (isMobile()) {
        if (!sidebar.classList.contains("collapsed")) {
            sidebarBackdrop.classList.remove("hidden");
        } else {
            sidebarBackdrop.classList.add("hidden");
        }
    }
});

// Close sidebar when backdrop is clicked
sidebarBackdrop.addEventListener("click", closeSidebarMobile);

// Close sidebar when any nav link is clicked on mobile
sidebar.querySelectorAll("nav a").forEach(link => {
    link.addEventListener("click", () => {
        if (isMobile()) {
            closeSidebarMobile();
        }
    });
});

// Collapse sidebar when resizing down to mobile
window.addEventListener("resize", () => {
    if (isMobile()) {
        closeSidebarMobile();
    } else {
        sidebarBackdrop.classList.add("hidden");
    }
});
