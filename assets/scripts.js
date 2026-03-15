// assets/scripts.js

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        renderizarGraficoDonut: function(dados) {
            // Se não houver dados, não faz nada
            if (!dados || dados.length === 0) {
                console.log("Sem dados para o gráfico.");
                return "";
            }

            // Aguarda o Dash terminar de montar o HTML
            setTimeout(() => {
                const canvas = document.getElementById('chart-donut-despesas');
                if (!canvas) return "";

                const ctx = canvas.getContext('2d');

                // Destrói gráfico anterior se existir para evitar sobreposição
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
                            borderWidth: 0,
                            hoverOffset: 10
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '80%', // Deixa o gráfico em formato de anel fino
                        plugins: {
                            legend: {
                                display: false // Legenda é feita pelo Python no HTML
                            },
                            tooltip: {
                                enabled: true
                            }
                        },
                        animation: {
                            animateScale: true,
                            animateRotate: true
                        }
                    }
                });
            }, 150); // 150ms é o tempo ideal de segurança

            return "";
        }
    }
});