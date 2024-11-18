function showContent(sectionId) {
    // Отримуємо всі елементи контенту
    const sections = document.querySelectorAll('.content-section');
    
    // Ховаємо всі секції
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Відображаємо лише вибрану секцію
    document.getElementById(sectionId).style.display = 'block';
}
