// Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api/tasks';

// State management
let tasks = [];
let currentTaskId = 1;

// Strategy descriptions
const strategyDescriptions = {
    smart_balance: "Balances all factors for optimal results",
    fastest_wins: "Prioritizes quick tasks for momentum",
    high_impact: "Focuses on high-importance work",
    deadline_driven: "Prioritizes by due dates"
};

// DOM Elements
const elements = {
    // Input elements
    strategySelect: document.getElementById('strategy'),
    strategyDescription: document.getElementById('strategyDescription'),
    taskForm: document.getElementById('taskForm'),
    taskTitle: document.getElementById('taskTitle'),
    dueDate: document.getElementById('dueDate'),
    estimatedHours: document.getElementById('estimatedHours'),
    importance: document.getElementById('importance'),
    importanceValue: document.getElementById('importanceValue'),
    dependencies: document.getElementById('dependencies'),
    tasksList: document.getElementById('tasksList'),
    jsonTextarea: document.getElementById('jsonTextarea'),
    
    // Buttons
    analyzeBtn: document.getElementById('analyzeBtn'),
    suggestBtn: document.getElementById('suggestBtn'),
    clearBtn: document.getElementById('clearBtn'),
    
    // Output elements
    loadingState: document.getElementById('loadingState'),
    errorState: document.getElementById('errorState'),
    errorMessage: document.getElementById('errorMessage'),
    emptyState: document.getElementById('emptyState'),
    resultsContainer: document.getElementById('resultsContainer'),
    strategyInfo: document.getElementById('strategyInfo'),
    warningsContainer: document.getElementById('warningsContainer'),
    tasksGrid: document.getElementById('tasksGrid')
};

// Initialize
function init() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    elements.dueDate.value = today;
    
    // Event listeners
    elements.strategySelect.addEventListener('change', updateStrategyDescription);
    elements.importance.addEventListener('input', updateImportanceValue);
    elements.taskForm.addEventListener('submit', handleAddTask);
    elements.analyzeBtn.addEventListener('click', handleAnalyzeTasks);
    elements.suggestBtn.addEventListener('click', handleGetSuggestions);
    elements.clearBtn.addEventListener('click', handleClearAll);
    
    console.log('🚀 Task Analyzer initialized');
}

// Tab switching
function switchTab(tab) {
    const formInput = document.getElementById('formInput');
    const jsonInput = document.getElementById('jsonInput');
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    if (tab === 'form') {
        formInput.classList.add('active');
        jsonInput.classList.remove('active');
        tabBtns[0].classList.add('active');
    } else {
        formInput.classList.remove('active');
        jsonInput.classList.add('active');
        tabBtns[1].classList.add('active');
    }
}

// Update strategy description
function updateStrategyDescription() {
    const strategy = elements.strategySelect.value;
    elements.strategyDescription.textContent = strategyDescriptions[strategy];
}

// Update importance value display
function updateImportanceValue() {
    elements.importanceValue.textContent = elements.importance.value;
}

// Handle add task from form
function handleAddTask(e) {
    e.preventDefault();
    
    const task = {
        id: currentTaskId++,
        title: elements.taskTitle.value,
        due_date: elements.dueDate.value,
        estimated_hours: parseInt(elements.estimatedHours.value),
        importance: parseInt(elements.importance.value),
        dependencies: parseDependencies(elements.dependencies.value)
    };
    
    tasks.push(task);
    renderTasksList();
    elements.taskForm.reset();
    
    // Reset to defaults
    const today = new Date().toISOString().split('T')[0];
    elements.dueDate.value = today;
    elements.importance.value = 5;
    updateImportanceValue();
    
    showToast(`✅ Task "${task.title}" added`, 'success');
}

// Parse dependencies input
function parseDependencies(input) {
    if (!input.trim()) return [];
    return input.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
}

// Render tasks list preview
function renderTasksList() {
    if (tasks.length === 0) {
        elements.tasksList.innerHTML = '';
        return;
    }
    
    elements.tasksList.innerHTML = tasks.map(task => `
        <div class="task-preview">
            <div class="task-preview-info">
                <div class="task-preview-title">${task.title}</div>
                <div class="task-preview-meta">
                    Due: ${formatDate(task.due_date)} | ${task.estimated_hours}h | Importance: ${task.importance}/10
                </div>
            </div>
            <button class="task-preview-remove" onclick="removeTask(${task.id})">Remove</button>
        </div>
    `).join('');
}

// Remove task
function removeTask(taskId) {
    tasks = tasks.filter(t => t.id !== taskId);
    renderTasksList();
    showToast('Task removed', 'info');
}

// Handle analyze tasks
async function handleAnalyzeTasks() {
    // Get tasks from appropriate source
    let tasksToAnalyze;
    
    const activeTab = document.querySelector('.input-mode.active');
    if (activeTab.id === 'jsonInput') {
        try {
            tasksToAnalyze = JSON.parse(elements.jsonTextarea.value);
            if (!Array.isArray(tasksToAnalyze)) {
                throw new Error('JSON must be an array');
            }
        } catch (err) {
            showError(`Invalid JSON: ${err.message}`);
            return;
        }
    } else {
        if (tasks.length === 0) {
            showError('Please add at least one task');
            return;
        }
        tasksToAnalyze = tasks;
    }
    
    const strategy = elements.strategySelect.value;
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasksToAnalyze,
                strategy: strategy
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Analysis failed');
        }
        
        const data = await response.json();
        displayResults(data, false);
        showToast('✅ Analysis complete', 'success');
        
    } catch (err) {
        showError(`Error: ${err.message}`);
        console.error('Analysis error:', err);
    }
}

// Handle get suggestions
async function handleGetSuggestions() {
    // Get tasks from appropriate source
    let tasksToAnalyze;
    
    const activeTab = document.querySelector('.input-mode.active');
    if (activeTab.id === 'jsonInput') {
        try {
            tasksToAnalyze = JSON.parse(elements.jsonTextarea.value);
            if (!Array.isArray(tasksToAnalyze)) {
                throw new Error('JSON must be an array');
            }
        } catch (err) {
            showError(`Invalid JSON: ${err.message}`);
            return;
        }
    } else {
        if (tasks.length === 0) {
            showError('Please add at least one task');
            return;
        }
        tasksToAnalyze = tasks;
    }
    
    const strategy = elements.strategySelect.value;
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasksToAnalyze,
                strategy: strategy
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Suggestion failed');
        }
        
        const data = await response.json();
        displaySuggestions(data);
        showToast('✨ Top suggestions ready', 'success');
        
    } catch (err) {
        showError(`Error: ${err.message}`);
        console.error('Suggestion error:', err);
    }
}

// Display results
function displayResults(data, isSuggestion = false) {
    hideLoading();
    elements.resultsContainer.classList.remove('hidden');
    elements.emptyState.classList.add('hidden');
    
    // Strategy info
    const strategyName = data.strategy_used.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    elements.strategyInfo.innerHTML = `
        <strong>Strategy:</strong> ${strategyName} | 
        <strong>Total Tasks:</strong> ${data.total_tasks || data.tasks.length}
    `;
    
    // Warnings
    if (data.warnings) {
        elements.warningsContainer.classList.remove('hidden');
        elements.warningsContainer.innerHTML = `
            <strong>⚠️ Warning:</strong> ${data.warnings.message}<br>
            <small>Tasks involved: ${data.warnings.circular_dependencies.join(', ')}</small>
        `;
    } else {
        elements.warningsContainer.classList.add('hidden');
    }
    
    // Render tasks
    const tasksToRender = data.tasks || [];
    elements.tasksGrid.innerHTML = tasksToRender.map(task => renderTaskCard(task)).join('');
}

// Display suggestions
function displaySuggestions(data) {
    hideLoading();
    elements.resultsContainer.classList.remove('hidden');
    elements.emptyState.classList.add('hidden');
    
    // Strategy info
    elements.strategyInfo.innerHTML = `
        <strong>💡 ${data.message}</strong>
    `;
    elements.warningsContainer.classList.add('hidden');
    
    // Render suggestions
    elements.tasksGrid.innerHTML = data.suggestions.map(suggestion => 
        renderSuggestionCard(suggestion)
    ).join('');
}

// Render task card
function renderTaskCard(task) {
    const priorityLevel = getPriorityLevel(task.priority_score);
    
    return `
        <div class="task-card priority-${priorityLevel}">
            <div class="task-header">
                <div>
                    <h3 class="task-title">${task.title}</h3>
                    <span class="priority-badge ${priorityLevel}">
                        ${priorityLevel.toUpperCase()} PRIORITY
                    </span>
                </div>
                <div class="task-score">${task.priority_score}</div>
            </div>
            
            <div class="task-details">
                <div class="task-detail">
                    <div class="task-detail-label">Due Date</div>
                    <div class="task-detail-value">${formatDate(task.due_date)}</div>
                </div>
                <div class="task-detail">
                    <div class="task-detail-label">Effort</div>
                    <div class="task-detail-value">${task.estimated_hours}h</div>
                </div>
                <div class="task-detail">
                    <div class="task-detail-label">Importance</div>
                    <div class="task-detail-value">${task.importance}/10</div>
                </div>
            </div>
            
            <div class="task-explanation">
                <strong>Why this score?</strong><br>
                ${task.explanation}
            </div>
        </div>
    `;
}

// Render suggestion card
function renderSuggestionCard(suggestion) {
    const task = suggestion.task;
    const priorityLevel = getPriorityLevel(suggestion.priority_score);
    
    return `
        <div class="task-card priority-${priorityLevel}">
            <div class="task-header">
                <div>
                    <h3 class="task-title">${task.title}</h3>
                    <span class="priority-badge ${priorityLevel}">
                        ${priorityLevel.toUpperCase()} PRIORITY
                    </span>
                </div>
                <div>
                    <div class="task-rank">#${suggestion.rank}</div>
                    <div class="task-score">${suggestion.priority_score}</div>
                </div>
            </div>
            
            <div class="task-details">
                <div class="task-detail">
                    <div class="task-detail-label">Due Date</div>
                    <div class="task-detail-value">${formatDate(task.due_date)}</div>
                </div>
                <div class="task-detail">
                    <div class="task-detail-label">Effort</div>
                    <div class="task-detail-value">${task.estimated_hours}h</div>
                </div>
                <div class="task-detail">
                    <div class="task-detail-label">Importance</div>
                    <div class="task-detail-value">${task.importance}/10</div>
                </div>
            </div>
            
            <div class="task-explanation">
                <strong>Analysis:</strong><br>
                ${suggestion.why_this_task}
            </div>
            
            <div class="task-recommendation">
                ${suggestion.recommendation}
            </div>
        </div>
    `;
}

// Get priority level based on score
function getPriorityLevel(score) {
    if (score >= 150) return 'high';
    if (score >= 80) return 'medium';
    return 'low';
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    date.setHours(0, 0, 0, 0);
    
    const diffTime = date - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return '🔥 Today';
    if (diffDays === 1) return '⏰ Tomorrow';
    if (diffDays === -1) return '⚠️ Yesterday';
    if (diffDays < 0) return `⚠️ ${Math.abs(diffDays)} days ago`;
    if (diffDays <= 7) return `📅 In ${diffDays} days`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Handle clear all
function handleClearAll() {
    if (confirm('Are you sure you want to clear all tasks?')) {
        tasks = [];
        currentTaskId = 1;
        renderTasksList();
        elements.jsonTextarea.value = '';
        hideResults();
        showToast('All tasks cleared', 'info');
    }
}

// UI State Management
function showLoading() {
    elements.loadingState.classList.remove('hidden');
    elements.errorState.classList.add('hidden');
    elements.emptyState.classList.add('hidden');
    elements.resultsContainer.classList.add('hidden');
}

function hideLoading() {
    elements.loadingState.classList.add('hidden');
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorState.classList.remove('hidden');
    elements.loadingState.classList.add('hidden');
    elements.emptyState.classList.add('hidden');
    elements.resultsContainer.classList.add('hidden');
}

function hideResults() {
    elements.resultsContainer.classList.add('hidden');
    elements.emptyState.classList.remove('hidden');
    elements.errorState.classList.add('hidden');
}

// Toast notifications
function showToast(message, type = 'info') {
    // Simple console log for now (you can enhance with a proper toast library)
    const emoji = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    console.log(`${emoji} ${message}`);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);