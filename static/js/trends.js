// Store chart instances
let charts = {};

// Nutrient targets for reference lines (Recommended Daily Allowances)
const targets = {
    calories: { rda: 2000, unit: 'kcal' },  // Based on 2000 calorie diet
    protein: { rda: 50, unit: 'g' },        // General RDA for adults
    carbohydrates: { rda: 130, unit: 'g' }, // ADA recommendation for diabetes
    total_fat: { rda: 65, unit: 'g' },      // Based on 2000 calorie diet (30%)
    sodium: { rda: 2300, unit: 'mg' },      // FDA recommendation
    fiber: { rda: 25, unit: 'g' }           // General recommendation for adults
};

async function loadTrendsData() {
    try {
        const response = await fetch(
            `${window.location.origin}/api/historical_totals/?user_id=${encodeURIComponent(userId)}&days=7`,
            {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayTrends(data);
    } catch (error) {
        console.error('Error loading trends data:', error);
        document.getElementById('trends-content').innerHTML = `
            <div class="text-red-500 p-4">Error loading trends data</div>
        `;
    }
}

function displayTrends(data) {
    const trendsContent = document.getElementById('trends-content');
    trendsContent.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg shadow-md p-4">
                <div id="caloriesChart"></div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-4">
                <div id="carbsChart"></div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-4">
                <div id="macrosChart"></div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-4">
                <div id="fiberChart"></div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-4">
                <div id="sodiumChart"></div>
            </div>
        </div>
    `;

    createCaloriesChart(data);
    createCarbsChart(data);
    createMacrosChart(data);
    createFiberChart(data);
    createSodiumChart(data);
    initializeTrendsWithRDA();
}

function createCaloriesChart(data) {
    const dates = data.map(d => d.date);
    const calories = data.map(d => d.calories);

    const trace1 = {
        x: dates,
        y: calories,
        name: 'Calories',
        type: 'scatter',
        line: { color: 'rgb(75, 192, 192)' }
    };

    const trace2 = {
        x: dates,
        y: Array(dates.length).fill(targets.calories.rda),
        name: 'RDA',
        type: 'scatter',
        line: {
            color: 'rgb(75, 192, 192)',
            dash: 'dash',
            width: 2
        }
    };

    const layout = {
        title: 'Daily Calories',
        yaxis: {
            title: targets.calories.unit,
            rangemode: 'tozero'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1.2
        }
    };

    Plotly.newPlot('caloriesChart', [trace1, trace2], layout);
}

function createCarbsChart(data) {
    const dates = data.map(d => d.date);
    const carbs = data.map(d => d.carbohydrates);

    const trace1 = {
        x: dates,
        y: carbs,
        name: 'Carbohydrates',
        type: 'scatter',
        line: { color: 'rgb(54, 162, 235)' }
    };

    const trace2 = {
        x: dates,
        y: Array(dates.length).fill(targets.carbohydrates.rda),
        name: 'Recommended Limit',
        type: 'scatter',
        line: {
            color: 'rgb(54, 162, 235)',
            dash: 'dash',
            width: 2
        }
    };

    const layout = {
        title: 'Daily Carbohydrates',
        yaxis: {
            title: targets.carbohydrates.unit,
            rangemode: 'tozero'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1.2
        }
    };

    Plotly.newPlot('carbsChart', [trace1, trace2], layout);
}

function createMacrosChart(data) {
    const dates = data.map(d => d.date);

    const traces = [
        {
            x: dates,
            y: data.map(d => d.protein),
            name: 'Protein',
            type: 'scatter',
            line: { color: 'rgb(255, 99, 132)' }
        },
        {
            x: dates,
            y: data.map(d => d.total_fat),
            name: 'Fat',
            type: 'scatter',
            line: { color: 'rgb(255, 206, 86)' }
        },
        {
            x: dates,
            y: Array(dates.length).fill(targets.protein.rda),
            name: 'Protein RDA',
            type: 'scatter',
            line: {
                color: 'rgb(255, 99, 132)',
                dash: 'dash',
                width: 2
            }
        },
        {
            x: dates,
            y: Array(dates.length).fill(targets.total_fat.rda),
            name: 'Fat RDA',
            type: 'scatter',
            line: {
                color: 'rgb(255, 206, 86)',
                dash: 'dash',
                width: 2
            }
        }
    ];

    const layout = {
        title: 'Protein & Fat',
        yaxis: {
            title: 'grams',
            rangemode: 'tozero'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1.2
        }
    };

    Plotly.newPlot('macrosChart', traces, layout);
}

function createFiberChart(data) {
    const dates = data.map(d => d.date);
    const fiber = data.map(d => d.fiber);

    const trace1 = {
        x: dates,
        y: fiber,
        name: 'Fiber',
        type: 'scatter',
        line: { color: 'rgb(153, 102, 255)' }
    };

    const trace2 = {
        x: dates,
        y: Array(dates.length).fill(targets.fiber.rda),
        name: 'RDA',
        type: 'scatter',
        line: {
            color: 'rgb(153, 102, 255)',
            dash: 'dash',
            width: 2
        }
    };

    const layout = {
        title: 'Daily Fiber',
        yaxis: {
            title: targets.fiber.unit,
            rangemode: 'tozero'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1.2
        }
    };

    Plotly.newPlot('fiberChart', [trace1, trace2], layout);
}

function createSodiumChart(data) {
    const dates = data.map(d => d.date);
    const sodium = data.map(d => d.sodium);

    const trace1 = {
        x: dates,
        y: sodium,
        name: 'Sodium',
        type: 'scatter',
        line: { color: 'rgb(255, 159, 64)' }
    };

    const trace2 = {
        x: dates,
        y: Array(dates.length).fill(targets.sodium.rda),
        name: 'RDA',
        type: 'scatter',
        line: {
            color: 'rgb(255, 159, 64)',
            dash: 'dash',
            width: 2
        }
    };

    const layout = {
        title: 'Daily Sodium',
        yaxis: {
            title: targets.sodium.unit,
            rangemode: 'tozero'
        },
        showlegend: true,
        legend: {
            x: 0,
            y: 1.2
        }
    };

    Plotly.newPlot('sodiumChart', [trace1, trace2], layout);
}

// Function to update RDA lines in the trends charts
function updateTrendsRDA(rdaValues) {
    const caloriesChart = document.getElementById('caloriesChart');
    const macronutrientsChart = document.getElementById('macrosChart');
    const carbsChart = document.getElementById('carbsChart');

    if (caloriesChart) {
        Plotly.update(caloriesChart, {}, {
            shapes: [{
                type: 'line',
                x0: '1900-01-01',
                x1: '2100-01-01',
                y0: rdaValues.calories,
                y1: rdaValues.calories,
                line: {
                    color: 'rgba(255, 0, 0, 0.5)',
                    width: 2,
                    dash: 'dash'
                }
            }]
        });
    }

    if (macronutrientsChart) {
        Plotly.update(macronutrientsChart, {}, {
            shapes: [
                {
                    type: 'line',
                    x0: '1900-01-01',
                    x1: '2100-01-01',
                    y0: rdaValues.protein,
                    y1: rdaValues.protein,
                    line: {
                        color: 'rgba(255, 0, 0, 0.5)',
                        width: 2,
                        dash: 'dash'
                    }
                },
                {
                    type: 'line',
                    x0: '1900-01-01',
                    x1: '2100-01-01',
                    y0: rdaValues.fat,
                    y1: rdaValues.fat,
                    line: {
                        color: 'rgba(255, 0, 0, 0.5)',
                        width: 2,
                        dash: 'dash'
                    }
                },
                {
                    type: 'line',
                    x0: '1900-01-01',
                    x1: '2100-01-01',
                    y0: rdaValues.fiber,
                    y1: rdaValues.fiber,
                    line: {
                        color: 'rgba(255, 0, 0, 0.5)',
                        width: 2,
                        dash: 'dash'
                    }
                }
            ]
        });
    }

    if (carbsChart) {
        Plotly.update(carbsChart, {}, {
            shapes: [{
                type: 'line',
                x0: '1900-01-01',
                x1: '2100-01-01',
                y0: rdaValues.carbohydrates,
                y1: rdaValues.carbohydrates,
                line: {
                    color: 'rgba(255, 0, 0, 0.5)',
                    width: 2,
                    dash: 'dash'
                }
            }]
        });
    }
}

// Load RDA values when initializing trends
function initializeTrendsWithRDA() {
    const savedRDA = localStorage.getItem(`rda_values_${userId}`);
    if (savedRDA) {
        const rdaValues = JSON.parse(savedRDA);
        updateTrendsRDA(rdaValues);
    }
}

// Function to toggle trends visibility
function toggleTrends() {
    const trendsSection = document.getElementById('trends-section');
    const isHidden = trendsSection.classList.contains('hidden');
    
    // Hide all sections first
    document.getElementById('main-content').classList.add('hidden');
    trendsSection.classList.add('hidden');
    
    // Show the trends section if it was hidden
    if (isHidden) {
        trendsSection.classList.remove('hidden');
        loadTrendsData();  // Load fresh data when showing trends
    } else {
        document.getElementById('main-content').classList.remove('hidden');
    }
}
