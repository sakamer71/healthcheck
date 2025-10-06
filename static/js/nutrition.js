// Nutrition-related functionality
const nutritionTargets = {
    calories: { min: 2300, max: 2500, unit: 'kcal' },
    total_fat: { min: 70, max: 90, unit: 'g' },
    carbohydrates: { min: 130, max: 150, unit: 'g' },
    protein: { min: 165, max: 200, unit: 'g' },
    sodium: { min: 0, max: 2300, unit: 'mg' },
    fiber: { min: 38, max: 50, unit: 'g' }
};

// Request lock to prevent concurrent submissions
let isSubmitting = false;

async function handleMealSubmission() {
    const mealText = mealInput.value.trim() || transcript.trim();
    if (!mealText || isSubmitting) return;

    try {
        isSubmitting = true;
        resultDiv.innerHTML = '<div class="text-center p-4"><i class="fas fa-spinner fa-spin"></i> Processing meal...</div>';

        const response = await fetch(
            `${window.location.origin}/api/calorie_count/${encodeURIComponent(mealText)}?user_id=${encodeURIComponent(window.userId)}`,
            {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Food data:', data);
        displayMealResult(data);
        clearInputs();
        
        // Update nutrition data after meal submission completes
        await updateNutritionData();
    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = '<div class="text-red-500 p-4">Error occurred while fetching calorie information.</div>';
    } finally {
        isSubmitting = false;
    }
}

function displayMealResult(data) {
    const healthMessage = data.health_analysis?.message || '';
    const isHealthy = data.health_analysis?.is_healthy;
    
    resultDiv.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-start space-x-4">
                ${data.image_url ? `
                    <div class="w-32 h-32 flex-shrink-0">
                        <img src="${data.image_url}" alt="${data.name}" class="w-full h-full object-cover rounded-lg">
                    </div>
                ` : ''}
                <div class="flex-grow">
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">${data.name}</h3>
                    <div class="text-sm text-gray-600 mb-4">Serving Size: ${data.serving_size}</div>
                    
                    <!-- Health Analysis Message -->
                    <div class="mb-4 p-3 rounded-lg ${isHealthy ? 'bg-green-50' : 'bg-yellow-50'}">
                        <div class="flex items-center">
                            <i class="fas ${isHealthy ? 'fa-check-circle text-green-500' : 'fa-info-circle text-yellow-500'} mr-2"></i>
                            <p class="${isHealthy ? 'text-green-700' : 'text-yellow-700'}">${healthMessage}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                ${createNutrientDisplay('Calories', data.calories, 'kcal')}
                ${createNutrientDisplay('Total Fat', data.total_fat, 'g')}
                ${createNutrientDisplay('Carbs', data.carbohydrates, 'g')}
                ${createNutrientDisplay('Protein', data.protein, 'g')}
                ${createNutrientDisplay('Fiber', data.fiber, 'g')}
                ${createNutrientDisplay('Sugars', data.sugars, 'g')}
                ${createNutrientDisplay('Sodium', data.sodium, 'mg')}
            </div>
        </div>
    `;
}

function createNutrientDisplay(label, value, unit) {
    return `
        <div class="bg-gray-50 rounded-lg p-3">
            <div class="text-sm text-gray-600">${label}</div>
            <div class="text-lg font-semibold text-gray-800">${value || 0}${unit}</div>
        </div>
    `;
}

async function updateNutritionData() {
    try {
        await Promise.all([
            updateDailyTotals(window.userId),
            updateMealList()
        ]);
    } catch (error) {
        console.error('Error updating nutrition data:', error);
    }
}

function clearInputs() {
    mealInput.value = '';
    transcript = '';
    transcriptDiv.textContent = '';
}

async function updateMealList() {
    try {
        console.log('Updating meal list...');
        const response = await fetch(
            `${window.location.origin}/api/daily_meals/?user_id=${encodeURIComponent(window.userId)}`,
            {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const meals = await response.json();
        console.log('Meals:', meals);

        // Update the meal list display
        const mealListDiv = document.getElementById('meal-list');
        if (!meals || meals.length === 0) {
            mealListDiv.innerHTML = '<p class="text-gray-500 text-center p-4">No meals logged today</p>';
            return;
        }

        mealListDiv.innerHTML = meals.map(meal => `
            <div class="bg-white rounded-lg shadow-md p-4 mb-4">
                <div class="flex items-start space-x-3">
                    ${meal.image_url ? `
                        <div class="w-16 h-16 flex-shrink-0">
                            <img src="${meal.image_url}" alt="${meal.name}" class="w-full h-full object-cover rounded-lg">
                        </div>
                    ` : ''}
                    <div class="flex-grow">
                        <div class="font-medium text-gray-800">${meal.name}</div>
                        <div class="text-sm text-gray-500">${meal.serving_size || 'No serving size'}</div>
                        <div class="text-sm text-gray-600 mt-1">
                            ${meal.calories}kcal • ${meal.protein}g protein • ${meal.total_fat}g fat
                        </div>
                    </div>
                    <button onclick="deleteMeal(${meal.id})" class="text-red-500 hover:text-red-700 ml-2">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error updating meal list:', error);
    }
}

function deleteMeal(mealId) {
    if (!confirm('Are you sure you want to delete this meal?')) {
        return;
    }
    
    console.log('Deleting meal:', mealId);
    fetch(
        `${window.location.origin}/api/meal/${mealId}?user_id=${encodeURIComponent(window.userId)}`,
        {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        }
    )
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        console.log('Meal deleted successfully');
        // Update the UI after successful deletion
        return updateNutritionData();
    })
    .catch(error => {
        console.error('Error deleting meal:', error);
        alert('Failed to delete meal. Please try again.');
    });
}

// Voice recognition setup
function setupVoiceRecognition() {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        microphoneIcon.classList.add('recording');
    };

    recognition.onspeechend = () => {
        recognition.stop();
        microphoneIcon.classList.remove('recording');
    };

    recognition.onresult = (event) => {
        try {
            transcript = event.results[0][0].transcript;
            console.log('User said:', transcript);
            transcriptDiv.textContent = transcript;
            mealInput.value = transcript;
        } catch (error) {
            console.error('Error in onresult:', error);
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        microphoneIcon.classList.remove('recording');
    };

    microphoneIcon.addEventListener('click', () => {
        recognition.start();
    });
}
