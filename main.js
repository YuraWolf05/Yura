let cart = {}; // Глобальна змінна для кошика

document.addEventListener("DOMContentLoaded", () => {
    cart = JSON.parse(localStorage.getItem("cart")) || {};
    const cartCount = document.getElementById("cart-count");

    // Функція для оновлення кількості товарів у кошику
    const updateCartCount = () => {
        const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
        if (cartCount) {
            cartCount.textContent = totalItems;
        }
    };

    // Функція для сповіщення користувача
    const showNotification = (message) => {
        const notification = document.createElement("div");
        notification.textContent = message;
        notification.style.position = "fixed";
        notification.style.bottom = "20px";
        notification.style.right = "20px";
        notification.style.background = "#000";
        notification.style.color = "#fff";
        notification.style.padding = "10px 15px";
        notification.style.borderRadius = "5px";
        notification.style.boxShadow = "0 4px 10px rgba(0, 0, 0, 0.2)";
        document.body.appendChild(notification);
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 2000);
    };

    // Делегування подій для кнопок +/- кількості
    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("increment")) {
            const quantitySpan = event.target.closest(".quantity-control").querySelector(".quantity");
            let value = parseInt(quantitySpan.textContent, 10) || 1;
            quantitySpan.textContent = value + 1;
        }

        if (event.target.classList.contains("decrement")) {
            const quantitySpan = event.target.closest(".quantity-control").querySelector(".quantity");
            let value = parseInt(quantitySpan.textContent, 10) || 1;
            if (value > 1) {
                quantitySpan.textContent = value - 1;
            }
        }
    });

    // Оновлення кількості товарів у кошику
    const updateCart = () => {
        cart = JSON.parse(localStorage.getItem("cart")) || {};
        updateCartCount();
    };

    // Функція для додавання товару до кошика через API
    const addToCartAPI = (productId, quantity, productName) => {
        fetch('/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    showNotification(`${productName} x${quantity} додано до кошика!`);
                } else {
                    console.error(data.message);
                    showNotification(`Помилка: ${data.message}`);
                }
            })
            .catch((error) => {
                console.error('Помилка при додаванні до кошика:', error);
                showNotification('Не вдалося додати товар до кошика.');
            });
    };

    // Обробка кліку по кнопці "Додати до кошика"
    const buyButtons = document.querySelectorAll(".buy");
    buyButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const productId = button.dataset.productId;
            const productName = button.dataset.productName;
            const productPrice = button.dataset.productPrice;

            const quantitySpan = button.closest(".product").querySelector(".quantity");
            const quantity = parseInt(quantitySpan.textContent, 10) || 1;

            if (quantity < 1) {
                alert("Кількість товару повинна бути більше 0!");
                return;
            }

            if (!cart[productId]) {
                cart[productId] = {
                    name: productName,
                    price: parseFloat(productPrice),
                    quantity: 0,
                };
            }
            cart[productId].quantity += quantity;

            localStorage.setItem("cart", JSON.stringify(cart));
            addToCartAPI(productId, quantity, productName);
            updateCartCount();
        });
    });

    updateCartCount();

    // Періодичне оновлення кошика
    setInterval(updateCart, 5000);
});

// Функція для перенаправлення на оплату через баночку Monobank
const redirectToMonobankJar = (cart) => {
    const totalAmount = Object.values(cart).reduce((sum, item) => sum + item.quantity * item.price, 0);
    const comment = encodeURIComponent("Оплата замовлення");
    const monobankJarUrl = `https://send.monobank.ua/jar/5UFNJXKthr?amount=${Math.floor(totalAmount)}&comment=${comment}`;
    window.location.href = monobankJarUrl;
};
