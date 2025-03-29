// CodeBug Analyzer - main.js

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('CodeBug Analyzer initialized');
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Handle form submission with loading state
    const analysisForm = document.getElementById('analysis-form');
    if (analysisForm) {
        analysisForm.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
            }
        });
    }
    
    // Initialize code snippet highlighting
    const codeElements = document.querySelectorAll('pre code');
    if (codeElements.length > 0) {
        highlightCodeSnippets(codeElements);
    }
});

// Simple function to add line numbers and basic highlighting to code snippets
function highlightCodeSnippets(elements) {
    elements.forEach(function(element) {
        const content = element.textContent;
        
        // Split into lines and add some basic syntax highlighting
        const lines = content.split('\n');
        let highlightedContent = '';
        
        lines.forEach(function(line, index) {
            // Add different background for highlighted line (usually line with error)
            const isHighlighted = line.includes(': ') && !line.includes('  ');
            const lineClass = isHighlighted ? 'highlighted-line' : '';
            
            // Very basic syntax highlighting
            let highlightedLine = line
                // Highlight keywords
                .replace(/\b(function|return|if|else|for|while|var|let|const|class|import|export|from|try|catch|throw|new|this|null|undefined|true|false)\b/g, '<span class="keyword">$1</span>')
                // Highlight strings
                .replace(/(["'])(.*?)\1/g, '<span class="string">$1$2$1</span>')
                // Highlight numbers
                .replace(/\b(\d+)\b/g, '<span class="number">$1</span>')
                // Highlight comments
                .replace(/(\/\/.*|\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>');
            
            highlightedContent += `<div class="${lineClass}">${highlightedLine}</div>`;
        });
        
        element.innerHTML = highlightedContent;
    });
}
