// CodeBug Analyzer - charts.js

/**
 * Initialize a pie chart showing bug severity distribution
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data with labels, values, and colors
 */
function initSeverityPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: data.colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff'
                    }
                },
                title: {
                    display: true,
                    text: 'Bug Severity Distribution',
                    color: '#fff'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize a horizontal bar chart showing most affected files
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data with labels and values
 */
function initTopFilesBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Number of Bugs',
                data: data.values,
                backgroundColor: '#3a86ff',
                borderColor: '#1e56a0',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Top Affected Files',
                    color: '#fff'
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Initialize a grouped bar chart showing language statistics
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data with labels, file_counts and bug_counts
 */
function initLanguageBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Number of Files',
                    data: data.file_counts,
                    backgroundColor: '#4cc9f0',
                    borderColor: '#3a86ff',
                    borderWidth: 1
                },
                {
                    label: 'Number of Bugs',
                    data: data.bug_counts,
                    backgroundColor: '#f72585',
                    borderColor: '#b5179e',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Language Distribution',
                    color: '#fff'
                },
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Initialize a bubble chart for bug density
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data with languages, file counts, bug counts, and bug densities
 */
function initBugDensityChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Prepare the bubble chart data
    const bubbleData = [];
    const colors = [
        '#f72585', '#b5179e', '#7209b7', '#560bad', '#480ca8', 
        '#3a0ca3', '#3f37c9', '#4361ee', '#4895ef', '#4cc9f0'
    ];
    
    data.labels.forEach((label, index) => {
        bubbleData.push({
            label: label,
            backgroundColor: colors[index % colors.length],
            borderColor: '#ffffff',
            data: [{
                x: data.file_counts[index],
                y: data.bug_counts[index],
                r: Math.min(20, Math.max(5, data.bug_densities[index] * 10))
            }]
        });
    });
    
    new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: bubbleData
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Bug Density by Language',
                    color: '#fff'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const x = context.raw.x;
                            const y = context.raw.y;
                            const r = context.raw.r / 10;
                            return [
                                `${label}:`,
                                `Files: ${x}`,
                                `Bugs: ${y}`,
                                `Density: ${r.toFixed(2)} bugs/file`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Number of Files',
                        color: '#fff'
                    },
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of Bugs',
                        color: '#fff'
                    },
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}
