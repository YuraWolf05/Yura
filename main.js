document.addEventListener("DOMContentLoaded", () => {
    // Ініціалізація кошика
    const cart = JSON.parse(localStorage.getItem("cart")) || {};
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

        // Обробка кнопок +/- для зміни кількості
        document.querySelectorAll(".quantity-control").forEach((control) => {
            const incrementBtn = control.querySelector(".increment");
            const decrementBtn = control.querySelector(".decrement");
            const quantitySpan = control.querySelector(".quantity");
    
            incrementBtn.addEventListener("click", () => {
                let value = parseInt(quantitySpan.textContent, 10) || 1;
                quantitySpan.textContent = value + 1;
            });
    
            decrementBtn.addEventListener("click", () => {
                let value = parseInt(quantitySpan.textContent, 10) || 1;
                if (value > 1) {
                    quantitySpan.textContent = value - 1;
                }
            });
        });    

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

            // Додаємо товар до локального кошика
            if (!cart[productId]) {
                cart[productId] = {
                    name: productName,
                    price: parseFloat(productPrice),
                    quantity: 0,
                };
            }
            cart[productId].quantity += quantity;

            // Оновлення даних у локальному сховищі
            localStorage.setItem("cart", JSON.stringify(cart));

            // Відправка даних на сервер
            addToCartAPI(productId, quantity, productName);

            // Оновлення кількості товарів у кошику
            updateCartCount();
        });
    });

    // Ініціалізація: оновлення кількості товарів у кошику
    updateCartCount();
});
