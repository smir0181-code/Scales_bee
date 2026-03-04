let chartInstance = null; // один график
let chartInstance2 = null



async function fetchData() {
    // Добавляем параметр timestamp, чтобы избежать кэширования
    const response = await fetch('/api/weight/history?hours=24&_=' + Date.now());
    return await response.json();
}

async function renderChart() {
    const data = await fetchData();
    const timestamps = data.map(d => new Date(d.timestamp).toLocaleString());
    const weights = data.map(d => d.weight_grams);

    const ctx = document.getElementById('weightChart').getContext('2d');
    const ctx2 = document.getElementById('weightChart2').getContext('2d')

    // Определяем актуальность данных
    const MAX_AGE_MINUTES = 1;                     // 10 минут
    const MAX_AGE_MS = MAX_AGE_MINUTES * 60 * 1000; // 600 000 мс
    let color = 'rgba(18, 0, 210, 0.8)';


    if (data.length > 0) {
        const lastEntry = data[data.length - 1];
        const lastTimestamp = new Date(lastEntry.timestamp).getTime();
        const now = Date.now();
        const ageMs = now - lastTimestamp; // сколько миллисекунд прошло с последнего измерения
        
        if (ageMs <= MAX_AGE_MS) {
            // Данные свежие (возраст не превышает порог) – показываем вес и время
            document.getElementById('currentWeight').textContent = lastEntry.weight_grams;
            document.getElementById('currentTime').textContent = new Date(lastEntry.timestamp).toLocaleString();

        }
        else {color= 'rgba(148, 146, 150, 0.3)'
            // Данные устарели (последнее измерение было слишком давно) – датчик вероятно отключён
            document.getElementById('currentWeight').textContent = '— (нет актуальных данных датчик вероятно отключён)';
            document.getElementById('currentTime').textContent = '—';
            
        }
    } else {
        // Данных вообще нет (например, новый улей без истории)
        document.getElementById('currentWeight').textContent = '—';
        document.getElementById('currentTime').textContent = '—';
        
    }

    // Далее код для отрисовки графика (уничтожение предыдущего и создание нового)
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    chartInstance = new Chart(ctx, {
        
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: 'Вес (граммы)',
                data: weights,
                borderColor: color,
                backgroundColor: 'rgba(183, 186, 185, 0.1)',
                
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Время' } },
                y: { title: { display: true, text: 'Вес (г)' } }
            }
        }
    });

    if (chartInstance2) {
        chartInstance2.destroy();
    }

    // Второй график: столбцы по суткам (одна колонка на дату, максимум за сутки)
    const dailyMap = {};
    for (const point of data) {
        const t = new Date(point.timestamp);
        const dateKey =
            t.getFullYear() + '-' +
            String(t.getMonth() + 1).padStart(2, '0') + '-' +
            String(t.getDate()).padStart(2, '0');

        // сохраняем максимальный вес за сутки
        if (!(dateKey in dailyMap)) {
            dailyMap[dateKey] = point.weight_grams;
        } else {
            dailyMap[dateKey] = Math.max(dailyMap[dateKey], point.weight_grams);
        }
    }

    const dailyLabels = Object.keys(dailyMap).sort();
    const dailyWeights = dailyLabels.map(d => dailyMap[d]);

    chartInstance2 = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: dailyLabels,
            datasets: [{
                label: 'Вес по суткам (г)',
                data: dailyWeights,
                borderColor: 'rgba(41, 29, 150, 0.9)',
                backgroundColor: 'rgba(41, 29, 150, 0.5)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                x: { title: { display: true, text: 'Дата' } },
                y: { title: { display: true, text: 'Вес (г)' } }
            }
        }
    });
}

// Первоначальная загрузка
renderChart();

// Обновление каждые 60 секунд (реальное значение, например 60000)
setInterval(renderChart, 6000);

// Кнопка очистки истории
document.getElementById('clearHistoryButton')?.addEventListener('click', async () => {
    const confirmed = confirm('Точно удалить всю историю измерений?');
    if (!confirmed) return;

    const response = await fetch('/api/weight/history/clear', { method: 'POST' });
    if (response.ok) {
        // Обновляем график после очистки
        await renderChart();
    } else {
        alert('Не удалось очистить историю');
    }
});