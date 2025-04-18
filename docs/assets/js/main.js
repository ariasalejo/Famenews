// main.js - Funciones globales y carga de noticias

document.addEventListener('DOMContentLoaded', function() {
    // Cargar las últimas noticias al cargar la página
    loadNews();
});

// Función para cargar noticias desde la API de Currents
function loadNews() {
    const apiKey = '8A-SQMIvfRxAXQ_d8AXQ_d8Y9AohCkUG2E5-7Vkf7IeQN_NhJ5w0EY';
    const url = `https://api.currentsapi.services/v1/latest-news?apiKey=${apiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => displayNews(data.news))
        .catch(error => console.error('Error fetching the news:', error));
}

// Función para mostrar las noticias en la página
function displayNews(news) {
    const newsContainer = document.getElementById('news-container');
    newsContainer.innerHTML = ''; // Limpiar contenido previo

    news.forEach(article => {
        const card = document.createElement('div');
        card.classList.add('card');

        card.innerHTML = `
            <img src="${article.image}" alt="Image">
            <div class="title">${article.title}</div>
            <div class="description">${article.description}</div>
            <a href="${article.url}" target="_blank">Leer más</a>
        `;

        newsContainer.appendChild(card);
    });
}
