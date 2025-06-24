/**
 * Аналитическая панель Wildberries
 * 
 * Основные функции:
 * 1. Загрузка и отображение данных о товарах
 * 2. Фильтрация товаров по цене, рейтингу и количеству отзывов
 * 3. Сортировка по различным полям
 * 4. Визуализация данных с помощью графиков
 * 5. Пагинация
 * 6. Автоматическое обновление данных каждые 30 секунд
 * 
 * Глобальные переменные:
 * - productsData: Массив товаров
 * - currentSort: Текущие параметры сортировки
 * - priceChart, discountChart: Объекты графиков
 * - currentPage, totalPages: Параметры пагинации
 * 
 * Основные функции:
 * - fetchData(): Загрузка данных с сервера
 * - initPriceSlider(): Инициализация слайдера цен
 * - renderTable(): Отрисовка таблицы товаров
 * - updateCharts(): Обновление графиков
 * - applyFilters(): Применение фильтров
 * 
 * Особенности:
 * - Автоматическое обновление данных каждые 30 секунд
 * - Сохранение состояния фильтров при обновлении страницы
 * - Адаптивный интерфейс
 */

let productsData = [];
let currentSort = { field: null, direction: 'asc' };
let priceChart = null;
let discountChart = null;
let currentPage = 1;
let totalPages = 1;
let totalItems = 0;
let absoluteMaxPrice = 0;

const tableBody = document.getElementById('productsTableBody');
const applyBtn = document.getElementById('applyFilters');
const priceRange = document.getElementById('priceRange');
const minPriceInput = document.getElementById('minPrice');
const maxPriceInput = document.getElementById('maxPrice');

document.addEventListener('DOMContentLoaded', async () => {
    try {
        absoluteMaxPrice = await fetchMaxPrice();
        
        initPriceSlider(absoluteMaxPrice);
        await fetchData(1, true);
        
        initCharts();
        updateCharts(productsData);
        
        setupEventListeners();
    } catch (e) {
        console.error("Initialization error:", e);
        if (tableBody) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4">Ошибка загрузки данных</td></tr>`;
        }
    }
});

function setupEventListeners() {
    // Кнопка применения фильтров
    if (applyBtn) {
        applyBtn.addEventListener('click', () => fetchData(1));
    }
    
    // Заголовки таблицы для сортировки
    document.querySelectorAll('.sortable').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            sortTable(e.currentTarget.dataset.sort);
        });
    });
    
    // Слайдер цен
    if (priceRange) {
        priceRange.addEventListener('input', () => {
            if (minPriceInput) minPriceInput.value = 0;
            if (maxPriceInput) maxPriceInput.value = priceRange.value;
        });
    }
    
    // Поле ввода максимальной цены
    if (maxPriceInput) {
        maxPriceInput.addEventListener('change', () => {
            if (priceRange) {
                priceRange.value = maxPriceInput.value;
            }
        });
    }
}

document.addEventListener('click', (e) => {
    // Обработка кликов по номерам страниц
    if (e.target.matches('#pagination .page-link[data-page]')) {
        e.preventDefault();
        const page = parseInt(e.target.dataset.page);
        fetchData(page);
    }
    
    // Обработка кнопки "Назад"
    const prevPage = document.getElementById('prevPage');
    if (prevPage && e.target.matches('#prevPage .page-link') && !prevPage.classList.contains('disabled')) {
        e.preventDefault();
        fetchData(currentPage - 1);
    }
    
    // Обработка кнопки "Вперед"
    const nextPage = document.getElementById('nextPage');
    if (nextPage && e.target.matches('#nextPage .page-link') && !nextPage.classList.contains('disabled')) {
        e.preventDefault();
        fetchData(currentPage + 1);
    }
});

async function fetchData(page = 1, initialLoad = false) {
    const loader = createLoader();
    loader.style.display = 'block';
    
    try {
        // Параметры запроса
        const params = new URLSearchParams({
            page: page,
            ordering: currentSort.field ? 
                `${currentSort.direction === 'desc' ? '-' : ''}${currentSort.field}` : ''
        });
        
        if (initialLoad) {
            if (maxPriceInput) {
                params.append('max_price', maxPriceInput.value);
            }
        } else {
            // Для последующих запросов берем значения из полей ввода
            const minPrice = minPriceInput ? minPriceInput.value : '';
            const maxPrice = maxPriceInput ? maxPriceInput.value : '';
            const minRating = document.getElementById('minRating')?.value || '';
            const minReviews = document.getElementById('minReviews')?.value || '';
            
            if (minPrice) params.append('min_price', minPrice);
            if (maxPrice) params.append('max_price', maxPrice);
            if (minRating) params.append('min_rating', minRating);
            if (minReviews) params.append('min_reviews', minReviews);
        }
        
        console.log('Fetching data with params:', params.toString());
        
        const response = await fetch(`/api/products/?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        
        const rawProducts = data.results || data;
        
        productsData = rawProducts.map(item => {
            return {
                id: item.id,
                name: item.name,
                price: parseFloat(item.price) || 0,
                discount_price: item.discount_price ? parseFloat(item.discount_price) : null,
                rating: item.rating ? parseFloat(item.rating) : null,
                reviews_count: item.reviews_count ? parseInt(item.reviews_count) : null,
                created_at: item.created_at
            };
        });
        
        // Обновление состояния пагинации
        currentPage = page;
        totalItems = data.count || productsData.length;
        const pageSize = data.results ? data.results.length : 10;
        totalPages = data.count > 0 ? Math.ceil(data.count / pageSize) : 1;
        
        renderTable(productsData);
        updateCharts(productsData);
        updatePaginationControls(totalItems, currentPage, totalPages);
        updateSortIndicators();
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        renderTable([]);
    } finally {
        loader.style.display = 'none';
    }
}

function updateSortIndicators() {
    document.querySelectorAll('.sortable').forEach(header => {
        header.classList.remove('asc', 'desc');
        if (header.dataset.sort === currentSort.field) {
            header.classList.add(currentSort.direction);
        }
    });
}

function updatePaginationControls(totalItems, currentPage, totalPages) {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;
    
    // Удаляет существующие элементы пагинации
    const existingPages = document.querySelectorAll('#pagination .page-item:not(#prevPage):not(#nextPage)');
    existingPages.forEach(el => el.remove());
    
    // Обновляет состояние кнопки "Назад"
    const prevPage = document.getElementById('prevPage');
    if (prevPage) {
        prevPage.classList.toggle('disabled', currentPage === 1);
    }
    
    // Добавляет номера страниц
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    const nextPageEl = document.getElementById('nextPage');
    if (nextPageEl) {
        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            paginationEl.insertBefore(li, nextPageEl);
        }
        
        // Обновляет состояние кнопки "Вперед"
        nextPageEl.classList.toggle('disabled', currentPage === totalPages);
    }
    
    // Обновляет информацию о странице
    const pageInfo = document.getElementById('pageInfo') || createPageInfoElement();
    pageInfo.textContent = `Показано ${productsData.length} из ${totalItems} товаров`;
}

function createPageInfoElement() {
    const pageInfo = document.createElement('div');
    pageInfo.id = 'pageInfo';
    pageInfo.className = 'text-muted page-info';
    
    const cardHeader = document.querySelector('.card-header');
    if (cardHeader) {
        cardHeader.appendChild(pageInfo);
    }
    
    return pageInfo;
}

function renderTable(data) {
    if (!tableBody) {
        console.error('Table body element not found');
        return;
    }
    
    if (data.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4">Нет данных для отображения</td></tr>`;
        return;
    }
    
    let html = '';
    for (const product of data) {
        html += `<tr>
            <td>${escapeHTML(product.name)}</td>
            <td>${product.price.toFixed(2)} ₽</td>
            <td>${product.discount_price !== null ? product.discount_price.toFixed(2) + ' ₽' : '-'}</td>
            <td>${product.rating !== null ? product.rating.toFixed(1) : '-'}</td>
            <td>${product.reviews_count !== null ? product.reviews_count : '-'}</td>
        </tr>`;
    }
    
    tableBody.innerHTML = html;
}

function escapeHTML(str) {
    return str.replace(/[&<>"']/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[tag] || tag));
}

async function fetchMaxPrice() {
    try {
        const response = await fetch('/api/max_price/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.max_price || 0;
    } catch (error) {
        console.error('Ошибка загрузки максимальной цены:', error);
        return 0;
    }
}

function initPriceSlider(maxPrice) {
    if (!priceRange || !minPriceInput || !maxPriceInput) {
        console.error('Price filter elements not found');
        return;
    }
    
    try {
        // Устанавливает максимальное значение для слайдера
        priceRange.max = maxPrice;
        maxPriceInput.placeholder = maxPrice.toFixed(0);
        
        // Устанавливает начальные значения
        priceRange.value = maxPrice;
        maxPriceInput.value = maxPrice;
        
        console.log('Slider initialized with max:', maxPrice);
    } catch (e) {
        console.error('Ошибка инициализации слайдера:', e);
    }
}

function sortTable(field) {
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'asc';
    }
    fetchData(1);
}

function initCharts() {
    const priceCtx = document.getElementById('priceHistogram')?.getContext('2d');
    const discountCtx = document.getElementById('discountRatingChart')?.getContext('2d');
    
    if (!priceCtx || !discountCtx) {
        console.warn('Chart canvases not found');
        return;
    }
    
    // Гистограмма цен
    priceChart = new Chart(priceCtx, {
        type: 'bar',
        data: { datasets: [{ data: [] }] },
        options: { 
            responsive: true, 
            plugins: { 
                title: { display: true, text: 'Распределение цен' },
                legend: { display: false }
            }
        }
    });
    
    // График скидка vs рейтинг
    discountChart = new Chart(discountCtx, {
        type: 'scatter',
        data: { datasets: [{ data: [] }] },
        options: { 
            responsive: true, 
            plugins: { 
                title: { display: true, text: 'Скидка vs Рейтинг' },
                legend: { display: false }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'Рейтинг' },
                    min: 0,
                    max: 5
                },
                y: { 
                    title: { display: true, text: 'Размер скидки (руб.)' },
                    beginAtZero: true
                }
            }
        }
    });
}

function createPriceRanges(data) {
    if (!data || data.length === 0) return {};
    
    const prices = data.map(p => p.price).filter(p => p > 0);
    if (prices.length === 0) return {};
    
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    
    const rangeCount = 5;
    const rangeSize = (maxPrice - minPrice) / rangeCount;
    
    const ranges = {};
    for (let i = 0; i < rangeCount; i++) {
        const start = Math.floor(minPrice + i * rangeSize);
        const end = Math.floor(minPrice + (i + 1) * rangeSize);
        const label = (i === rangeCount - 1) ? 
            `${start}+` : 
            `${start}-${end}`;
        ranges[label] = 0;
    }
    
    return ranges;
}

function updateCharts(data) {
    // Гистограмма цен
    const priceRanges = createPriceRanges(data);
    
    if (Object.keys(priceRanges).length > 0) {
        Object.keys(priceRanges).forEach(range => {
            if (range.includes('-')) {
                const [min, max] = range.split('-').map(Number);
                priceRanges[range] = data.filter(p => p.price >= min && p.price <= max).length;
            } else if (range.endsWith('+')) {
                const min = parseInt(range);
                priceRanges[range] = data.filter(p => p.price >= min).length;
            }
        });
        
        priceChart.data.labels = Object.keys(priceRanges);
        priceChart.data.datasets[0].data = Object.values(priceRanges);
        priceChart.data.datasets[0].label = `Товары (${data.length})`;
        priceChart.update();
    }
    
    // График "Скидка vs Рейтинг"
    const discountData = data
        .filter(p => p.rating !== null && p.discount_price !== null && p.price > p.discount_price)
        .map(p => ({
            x: p.rating,
            y: p.price - p.discount_price
        }));
    
    discountChart.data.datasets[0].data = discountData;
    discountChart.data.datasets[0].label = `Товары со скидкой (${discountData.length})`;
    
    if (discountData.length > 0) {
        const discounts = discountData.map(d => d.y);
        discountChart.options.scales.y.max = Math.max(...discounts) * 1.1;
    }
    
    if (discountChart) {
        discountChart.update();
    }
}

// Обновление данных каждые 30 секунд
setInterval(async () => {
    await fetchData(currentPage);
}, 30000);

function applyFilters() {
    fetchData(1);
}

function createLoader() {
    let loader = document.getElementById('loader');
    
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'loader';
        loader.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            display: none;
        `;
        loader.innerHTML = `
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
            <span class="ms-2">Загрузка данных...</span>
        `;
        document.body.appendChild(loader);
    }
    
    return loader;
}