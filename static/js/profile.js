// Profile data management
let profileData = {};

// Load profile data from localStorage
function loadProfileData() {
    // Get userId from the global scope (window object)
    const userId = window.userId;
    const savedProfile = localStorage.getItem(`profile_${userId}`);
    if (savedProfile) {
        profileData = JSON.parse(savedProfile);
        updateFormWithProfile();
    }
}

// Update form fields with profile data
function updateFormWithProfile() {
    if (Object.keys(profileData).length === 0) return;

    document.getElementById('profile-name').value = profileData.name || '';
    document.getElementById('profile-age').value = profileData.age || '';
    
    // Handle height in ft and inches
    if (profileData.heightFt) {
        document.getElementById('profile-height-ft').value = profileData.heightFt;
        document.getElementById('profile-height-in').value = profileData.heightIn || 0;
    }
    
    document.getElementById('profile-weight').value = profileData.weight || '';
    document.getElementById('profile-target-weight').value = profileData.targetWeight || '';
    document.getElementById('profile-target-date').value = profileData.targetDate || '';
    document.getElementById('profile-activity').value = profileData.activityLevel || 'sedentary';
}

// Convert height to cm for calculations
function heightToCm(feet, inches) {
    const totalInches = (feet * 12) + (inches || 0);
    return Math.round(totalInches * 2.54);
}

// Convert weight to kg for calculations
function lbsToKg(lbs) {
    return Math.round(lbs * 0.45359237 * 10) / 10;
}

// Save profile data
function saveProfileData(formData) {
    // Get userId from the global scope (window object)
    const userId = window.userId;
    profileData = formData;
    localStorage.setItem(`profile_${userId}`, JSON.stringify(formData));
    
    // Update the display name in the header
    if (typeof updateDisplayName === 'function') {
        updateDisplayName();
    }
}

// Update RDA values based on profile
async function updateRDAValues(formData) {
    try {
        const response = await fetch('/api/calculate-rda', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                age: formData.age,
                heightCm: formData.heightCm,
                weightKg: formData.weightKg,
                targetWeightKg: formData.targetWeightKg,
                targetDate: formData.targetDate,
                activityLevel: formData.activityLevel
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get RDA values');
        }

        const rdaValues = await response.json();
        
        // Store RDA values in localStorage
        localStorage.setItem(`rda_values_${window.userId}`, JSON.stringify(rdaValues));
        
        // Update the trends visualization with new RDA values
        if (typeof updateTrendsRDA === 'function') {
            updateTrendsRDA(rdaValues);
        }

        // Update daily totals with new targets
        if (typeof updateDailyTotals === 'function') {
            updateDailyTotals(window.userId);
        }

        // Show a notification with the new values
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded shadow-lg';
        notification.innerHTML = `
            <p class="font-bold">Your Daily Recommended Values:</p>
            <ul class="mt-2">
                <li>Calories: ${rdaValues.calories} kcal</li>
                <li>Protein: ${rdaValues.protein}g</li>
                <li>Fat: ${rdaValues.fat}g</li>
                <li>Fiber: ${rdaValues.fiber}g</li>
                <li>Carbohydrates: ${rdaValues.carbohydrates}g</li>
            </ul>
        `;
        document.body.appendChild(notification);
        
        // Remove notification after 10 seconds
        setTimeout(() => {
            notification.remove();
        }, 10000);

    } catch (error) {
        console.error('Error updating RDA values:', error);
    }
}

// Toggle profile modal visibility
function toggleProfileModal() {
    const modal = document.getElementById('profile-modal');
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        loadProfileData();
    } else {
        modal.classList.add('hidden');
    }
}

// Handle form submission
document.getElementById('profile-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('profile-name').value,
        age: parseInt(document.getElementById('profile-age').value),
        heightFt: parseInt(document.getElementById('profile-height-ft').value),
        heightIn: parseInt(document.getElementById('profile-height-in').value) || 0,
        heightCm: heightToCm(
            parseInt(document.getElementById('profile-height-ft').value),
            parseInt(document.getElementById('profile-height-in').value) || 0
        ),
        weight: parseFloat(document.getElementById('profile-weight').value),
        weightKg: lbsToKg(parseFloat(document.getElementById('profile-weight').value)),
        targetWeight: parseFloat(document.getElementById('profile-target-weight').value),
        targetWeightKg: lbsToKg(parseFloat(document.getElementById('profile-target-weight').value)),
        targetDate: document.getElementById('profile-target-date').value,
        activityLevel: document.getElementById('profile-activity').value
    };

    saveProfileData(formData);
    
    // Update RDA values before closing the modal
    await updateRDAValues(formData);
    
    toggleProfileModal();
});
