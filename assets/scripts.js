window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        renderizarGraficoDonut: function(dados) {
            const canvas = document.getElementById('chart-donut-despesas');
            if (!canvas || !dados || dados.length === 0) return "";

            const ctx = canvas.getContext('2d');
            if (window.meuGraficoDonut) {
                window.meuGraficoDonut.destroy();
            }

            window.meuGraficoDonut = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: dados.map(item => item.categoria),
                    datasets: [{
                        data: dados.map(item => item.valor),
                        backgroundColor: dados.map(item => item.cor_hex),
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '80%', // Visual de anel do seu design
                    plugins: { legend: { display: false } }
                }
            });
            return "";
        }
    }
});