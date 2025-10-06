// Meal list functionality
async function updateMealList() {
    try {
        const url = `${window.location.origin}/api/daily_meals/?user_id=${encodeURIComponent(userId)}`;
        console.log('Fetching meals from:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const meals = await response.json();
        console.log(`Received ${meals.length} meals for today:`, meals);
        displayMealList(meals);
    } catch (error) {
        console.error('Error fetching meal list:', error);
        document.getElementById('meal-list').innerHTML = `
            <div class="text-red-500 text-sm">Error loading meals</div>
        `;
    }
}

async function deleteMeal(mealId, event) {
    if (!event || !mealId) {
        console.error('Missing event or mealId in deleteMeal');
        return;
    }
    
    event.stopPropagation();  // Prevent the meal details from toggling
    console.log('Deleting meal:', mealId);
    
    try {
        const url = `${window.location.origin}/api/meal/${mealId}?user_id=${encodeURIComponent(userId)}`;
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Refresh the meal list and daily totals
        await updateMealList();
        await updateDailyTotals(userId);
    } catch (error) {
        console.error('Error deleting meal:', error);
        alert('Failed to delete meal. Please try again.');
    }
}

function displayMealList(meals) {
    const mealListDiv = document.getElementById('meal-list');
    console.log(`Displaying ${meals?.length || 0} meals in meal list`);
    
    if (!meals || meals.length === 0) {
        mealListDiv.innerHTML = `
            <div class="text-gray-500 text-sm italic">No meals recorded today</div>
        `;
        return;
    }

    // Sort meals by timestamp in descending order (newest first)
    const sortedMeals = [...meals].sort((a, b) => b.timestamp - a.timestamp);
    console.log('Meals after sorting:', sortedMeals.map(m => ({ name: m.name, time: new Date(m.timestamp * 1000).toLocaleTimeString() })));

    mealListDiv.innerHTML = sortedMeals.map(meal => {
        const time = new Date(meal.timestamp * 1000).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
        return `
            <div class="bg-white rounded-lg shadow-sm p-3 mb-2">
                <div class="flex flex-col">
                    <div class="flex justify-between items-start mb-1">
                        <div class="font-medium text-gray-800">${meal.name}</div>
                        <div class="text-xs text-gray-500">${time}</div>
                    </div>
                    <div class="flex flex-wrap gap-2 text-xs text-gray-500">
                        <span>${meal.calories} cal</span>
                        <span>${meal.carbohydrates}g carbs</span>
                        <span>${meal.protein}g protein</span>
                        <span>${meal.total_fat}g fat</span>
                    </div>
                    <div class="flex justify-end mt-1">
                        <button onclick="deleteMeal('${meal.id}', event)" 
                                class="text-gray-400 hover:text-red-500 transition-colors p-1">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function createMealDetailRow(label, value, unit) {
    return `
        <div class="flex justify-between items-center py-1">
            <span class="text-gray-600">${label}:</span>
            <span class="font-medium text-gray-800">${value}${unit}</span>
        </div>
    `;
}

// Initialize the meal list when the script loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Meal list script loaded, initializing...');
    if (window.userId) {
        updateMealList();
    } else {
        console.log('Waiting for userId to be available...');
        // Wait for userId to be available
        const checkUserId = setInterval(() => {
            if (window.userId) {
                clearInterval(checkUserId);
                updateMealList();
            }
        }, 100);
    }
});
