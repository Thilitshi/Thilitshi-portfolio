const chatButton = document.getElementById("chat-button");
const chatbot = document.querySelector(".chatbot");
const closeChat = document.getElementById("close-chat");
const sendButton = document.getElementById("send-button");
const messageInput = document.getElementById("message-input");
const chatMessages = document.getElementById("chat-messages");

chatButton.addEventListener("click", () => {
    chatbot.classList.add("active");
    messageInput.focus();
});

closeChat.addEventListener("click", () => {
    chatbot.classList.remove("active");
});

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

function addMessage(message, type) {
    const div = document.createElement("div");

    div.className = type === "user"
        ? "user-message"
        : "bot-message";

    div.textContent = message;

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) return;

    addMessage(message, "user");

    messageInput.value = "";
    sendButton.disabled = true;

    const loading = document.createElement("div");
    loading.className = "bot-message";
    loading.textContent = "Thinking...";

    chatMessages.appendChild(loading);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/api/chat",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            }
        );

        const responseText = await response.text();

        console.log("Status:", response.status);
        console.log("Response:", responseText);

        loading.remove();

        if (!response.ok) {
            let errorMessage = "Server error.";

            try {
                const errorData = JSON.parse(responseText);

                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (error) {
                console.error(error);
            }

            addMessage(
                "Sorry, there was a problem: " + errorMessage,
                "bot"
            );

            return;
        }

        const data = JSON.parse(responseText);

        addMessage(
            data.response || "I couldn't generate a response.",
            "bot"
        );

    } catch (error) {
        loading.remove();

        console.error("FETCH ERROR:", error);

        addMessage(
            "Sorry, I couldn't connect to the server.",
            "bot"
        );

    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

const animatedSections = document.querySelectorAll(
    "#techstack, #projects, #certifications"
);

const observer = new IntersectionObserver(
    (entries, observer) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
                observer.unobserve(entry.target);
            }
        });
    },
    {
        threshold: 0.15
    }
);

animatedSections.forEach((section) => {
    observer.observe(section);
});