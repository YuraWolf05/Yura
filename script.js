function showContent(sectionId) {
    // Перевіряємо, чи елемент існує
    const section = document.getElementById(sectionId);
    if (!section) {
        console.error(`Секція з ID "${sectionId}" не знайдена.`);
        return;
    }
    
    // Ховаємо всі секції
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });

    // Відображаємо лише вибрану секцію
    section.style.display = 'block';

    document.getElementById('profile-link').addEventListener('click', (event) => {
        console.log('Перехід на профіль:', event.target.href);
    });
}

// Фунція для кнопки - 1 +  кількості товару.
function initializeQuantityControls() {
    const controls = document.querySelectorAll('.quantity-control');

    controls.forEach(control => {
        const decrementButton = control.querySelector('.decrement');
        const incrementButton = control.querySelector('.increment');
        const quantityDisplay = control.querySelector('.quantity');

        let quantity = parseInt(quantityDisplay.textContent, 10); // Початкове значення з HTML

        // Зменшення
        decrementButton.addEventListener('click', () => {
            if (quantity > 1) {
                quantity--;
                quantityDisplay.textContent = quantity;
            }
        });

        // Збільшення
        incrementButton.addEventListener('click', () => {
            quantity++;
            quantityDisplay.textContent = quantity;
        });
    });
}
