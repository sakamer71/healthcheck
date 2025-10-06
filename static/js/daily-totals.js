// Daily totals functionality
async function updateDailyTotals(userId) {
    try {
        const response = await fetch(
            `${window.location.origin}/api/daily_totals/?user_id=${encodeURIComponent(userId)}`,
            {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Daily totals:', data);
        displayDailyTotals(data, userId);
    } catch (error) {
        console.error('Error fetching daily totals:', error);
        document.getElementById('daily-totals').textContent = 'Error fetching daily totals.';
    }
}

function getNutritionTargets(userId) {
    // Try to get personalized RDA values from localStorage
    const rdaValues = localStorage.getItem(`rda_values_${userId}`);
    if (rdaValues) {
        const rda = JSON.parse(rdaValues);
        return {
            calories: { min: Math.round(rda.calories * 0.9), max: rda.calories, unit: 'kcal' },
            protein: { min: Math.round(rda.protein * 0.8), max: rda.protein, unit: 'g' },
            fat: { min: Math.round(rda.fat * 0.8), max: rda.fat, unit: 'g' },
            fiber: { min: Math.round(rda.fiber * 0.8), max: rda.fiber, unit: 'g' },
            carbohydrates: { min: Math.round(rda.carbohydrates * 0.8), max: rda.carbohydrates, unit: 'g' }
        };
    }

    // Default values if no personalized RDA exists
    return {
        calories: { min: 1800, max: 2000, unit: 'kcal' },
        protein: { min: 45, max: 50, unit: 'g' },
        fat: { min: 65, max: 70, unit: 'g' },
        fiber: { min: 20, max: 25, unit: 'g' },
        carbohydrates: { min: 270, max: 300, unit: 'g' }
    };
}

function displayDailyTotals(data, userId) {
    const dailyTotalsDiv = document.getElementById('daily-totals');
    const targets = getNutritionTargets(userId);
    
    // Map the API response keys to our target keys
    const mappedData = {
        calories: data.calories || 0,
        protein: data.protein || 0,
        fat: data.total_fat || 0,  // Note the key difference
        fiber: data.fiber || 0,
        carbohydrates: data.carbohydrates || 0
    };

    const nutritionHtml = Object.entries(targets).map(([key, target]) => {
        const value = mappedData[key] || 0;
        const percentage = (value / target.max) * 100;
        const status = getProgressStatus(value, target);

        return `
            <div class="bg-white rounded-lg shadow-sm p-4">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-sm font-medium text-gray-600">
                        ${formatNutrientName(key)}
                    </span>
                    <span class="text-sm font-semibold ${status.textColor}">
                        ${value}${target.unit}
                    </span>
                </div>
                <div class="relative pt-1">
                    <div class="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                        <div class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${status.bgColor}"
                             style="width: ${Math.min(percentage, 100)}%">
                        </div>
                    </div>
                </div>
                <div class="flex justify-between mt-1">
                    <span class="text-xs text-gray-500">
                        Target: ${target.min}-${target.max}${target.unit}
                    </span>
                    <span class="text-xs ${status.textColor}">
                        ${Math.round(percentage)}%
                    </span>
                </div>
            </div>
        `;
    }).join('');

    dailyTotalsDiv.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">Daily Totals</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                ${nutritionHtml}
            </div>
        </div>
    `;
}

function getProgressStatus(value, target) {
    const percentage = (value / target.max) * 100;
    
    if (percentage <= 80) {
        return {
            bgColor: 'bg-green-500',
            textColor: 'text-green-600'
        };
    }
    if (percentage <= 110) {
        return {
            bgColor: 'bg-orange-500',
            textColor: 'text-orange-600'
        };
    }
    return {
        bgColor: 'bg-red-500',
        textColor: 'text-red-600'
    };
}

function formatNutrientName(key) {
    return key.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
