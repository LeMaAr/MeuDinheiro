window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        renderizarGraficoDonut: function(dados) {
            const canvas = document.getElementById('chart-donut-despesas');
            if (!canvas || !dados || dados.length === 0) return;

            const ctx = canvas.getContext('2d');

            if (window.meuGraficoDonut) {
                window.meuGraficoDonut.destroy();
            }

            const labels = dados.map(item => item.categoria);
            const valores = dados.map(item => item.valor);
            const cores = dados.map(item => item.cor_hex);

            window.meuGraficoDonut = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: valores,
                        backgroundColor: cores,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '80%',
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        } // Fechamento da função
    } // Fechamento do objeto clientside
});