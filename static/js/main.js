/* Rara Jewelry - Premium Luxury Client Actions JS */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Initialize Product Image Thumbnails switcher
    const thumbnails = document.querySelectorAll(".thumb-img");
    const mainProductImage = document.getElementById("mainProductImage");

    if (thumbnails.length > 0 && mainProductImage) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener("click", function () {
                // Clear active states
                thumbnails.forEach(t => t.classList.remove("active"));
                // Activate clicked
                this.classList.add("active");
                // Update main preview source
                mainProductImage.src = this.src;
                // If zoom is enabled, update data attribute too
                if (mainProductImage.parentElement.classList.contains("zoom-container")) {
                    // Reset zoom transformations if any
                    mainProductImage.style.transform = "scale(1)";
                }
            });
        });
    }

    // 2. Premium Image Zoom on Hover effect
    const zoomContainer = document.querySelector(".zoom-container");
    if (zoomContainer && mainProductImage) {
        zoomContainer.addEventListener("mousemove", function (e) {
            const rect = e.currentTarget.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position within element
            const y = e.clientY - rect.top;  // y position within element

            const xPercent = (x / rect.width) * 100;
            const yPercent = (y / rect.height) * 100;

            mainProductImage.style.transformOrigin = `${xPercent}% ${yPercent}%`;
            mainProductImage.style.transform = "scale(2)";
        });

        zoomContainer.addEventListener("mouseleave", function () {
            mainProductImage.style.transform = "scale(1)";
            mainProductImage.style.transformOrigin = "center center";
        });
    }

    // 3. Wishlist AJAX toggler
    const wishlistButtons = document.querySelectorAll(".ajax-wishlist-toggle");
    wishlistButtons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const productId = this.getAttribute("data-product-id");
            const heartIcon = this.querySelector("i");

            if (!productId) return;

            fetch(`/wishlist/toggle/${productId}/`, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
                .then(response => {
                    if (response.status === 401 || response.url.includes("login")) {
                        // Not authenticated, redirect to login
                        window.location.href = `/accounts/login/?next=${window.location.pathname}`;
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.status === "success" || data.added !== undefined) {
                        if (data.added) {
                            heartIcon.classList.remove("fa-regular");
                            heartIcon.classList.add("fa-solid");
                            heartIcon.classList.add("text-gold");
                        } else {
                            heartIcon.classList.remove("fa-solid");
                            heartIcon.classList.remove("text-gold");
                            heartIcon.classList.add("fa-regular");
                        }

                        // Show a toast or direct alert
                        showTemporaryToast(data.message);

                        // Dynamically increment/decrement wishlist badges if present
                        const badges = document.querySelectorAll(".badge-wishlist");
                        badges.forEach(b => {
                            let val = parseInt(b.innerText || "0");
                            val = data.added ? val + 1 : Math.max(val - 1, 0);
                            b.innerText = val;
                            b.style.display = val === 0 ? "none" : "inline-block";
                        });
                    }
                })
                .catch(err => console.error("Wishlist AJAX error:", err));
        });
    });

    // Helper: Dynamic Toast notification builder
    function showTemporaryToast(message) {
        const toastContainer = document.createElement("div");
        toastContainer.className = "position-fixed bottom-0 start-0 p-3";
        toastContainer.style.zIndex = "1050";

        toastContainer.innerHTML = `
            <div class="toast show bg-black border-gold text-light" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-dark text-gold border-gold-dim">
                    <i class="fa-solid fa-gem me-2"></i>
                    <strong class="me-auto">Rara Jewelry</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body text-xs">
                    ${message}
                </div>
            </div>
        `;
        document.body.appendChild(toastContainer);
        setTimeout(() => {
            toastContainer.remove();
        }, 3500);
    }
});
