document.querySelectorAll("[data-save-button]").forEach((button) => {
    button.addEventListener("click", async () => {
        const card = button.closest("[data-bubble-id]");
        const bubbleId = card.dataset.bubbleId;
        button.disabled = true;

        try {
            const response = await fetch(`/api/bubbles/${bubbleId}/toggle`, {
                method: "POST",
                headers: { "Accept": "application/json" }
            });

            if (!response.ok) throw new Error("Unable to update bubble");

            const data = await response.json();
            button.classList.toggle("saved", data.saved);
            button.querySelector(".heart").textContent = data.saved ? "♥" : "♡";
            button.querySelector(".save-label").textContent = data.saved ? "Saved" : "Save bubble";
        } catch (error) {
            alert("Something went wrong. Please try again.");
        } finally {
            button.disabled = false;
        }
    });
});
