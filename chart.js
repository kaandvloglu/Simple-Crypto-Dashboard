// chart.js dosyası

// İlk coin için başlangıç verileri
var initialData = { coins,[0]:sparkline_in_7d.price | tojson | safe };

// Coin isimleri ve ID'leri için de bir dizi alalım
var coinIds = { coins, map(attribute='id') { list | tojson | safe }};

// Chart.js ile ilk coin grafiğini oluştur
var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: initialData.map((_, index) => index), // X ekseni için basit indeksler
        datasets: [{
            label: 'Coin Price (USD)',
            data: initialData,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    }
});

// Bu fonksiyon AJAX ile yeni verileri alıp grafiği güncelleyecek
function updateChart() {
    var selectedCoinId = document.getElementById('coin-select').value;

    fetch(`/get-coin-data?coin=${selectedCoinId}`)
        .then(response => response.json())
        .then(data => {
            myChart.data.labels = data.labels;
            myChart.data.datasets[0].data = data.prices;
            myChart.update();
        });
}


