/**
 * Security utilities for XSS prevention
 */

/**
 * Escapes HTML entities to prevent XSS attacks
 * @param {string} unsafe - The string to escape
 * @returns {string} - The escaped string safe for HTML
 */
function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') {
        return String(unsafe);
    }
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "<")
        .replace(/>/g, ">")
        .replace(/"/g, """)
        .replace(/'/g, "&#039;");
}

/**
 * Sanitizes job data for safe HTML rendering
 * @param {object} job - The job object to sanitize
 * @returns {object} - Sanitized job object
 */
function sanitizeJobData(job) {
    const sanitized = {};
    for (const [key, value] of Object.entries(job)) {
        if (typeof value === 'string') {
            sanitized[key] = escapeHtml(value);
        } else if (Array.isArray(value)) {
            sanitized[key] = value.map(item => escapeHtml(item));
        } else {
            sanitized[key] = value;
        }
    }
    return sanitized;
}

/**
 * Creates a safe DOM element with sanitized content
 * @param {string} tagName - The HTML tag name
 * @param {object} attributes - Element attributes
 * @param {string} textContent - Text content (will be escaped)
 * @returns {HTMLElement} - Safe DOM element
 */
function createSafeElement(tagName, attributes = {}, textContent = '') {
    const element = document.createElement(tagName);
    
    for (const [key, value] of Object.entries(attributes)) {
        element.setAttribute(key, value);
    }
    
    if (textContent) {
        element.textContent = textContent;
    }
    
    return element;
}

/**
 * Safely renders job HTML using DOM manipulation instead of innerHTML
 * @param {object} job - The job object to render
 * @returns {HTMLElement} - Safe job card element
 */
function createSafeJobCard(job) {
    const sanitizedJob = sanitizeJobData(job);
    
    const card = createSafeElement('div', {
        className: 'bg-white p-6 rounded-lg shadow border'
    });
    
    const header = createSafeElement('div', {
        className: 'flex justify-between items-start'
    });
    
    const titleSection = createSafeElement('div');
    const roleTitle = createSafeElement('h3', {
        className: 'text-xl font-semibold text-gray-900'
    }, sanitizedJob.role);
    const companyName = createSafeElement('p', {
        className: 'text-lg text-blue-600'
    }, sanitizedJob.company);
    
    titleSection.appendChild(roleTitle);
    titleSection.appendChild(companyName);
    
    const sourceBadge = createSafeElement('span', {
        className: 'bg-green-100 text-green-800 px-2 py-1 rounded text-sm'
    }, sanitizedJob.source_platform);
    
    header.appendChild(titleSection);
    header.appendChild(sourceBadge);
    
    const details = createSafeElement('div', {
        className: 'mt-4 space-y-2'
    });
    
    const techStack = createSafeElement('p', {}, 
        `Tech Stack: ${sanitizedJob.tech_stack.join(', ') || 'Not specified'}`);
    const location = createSafeElement('p', {}, 
        `Location: ${sanitizedJob.location}`);
    const salary = createSafeElement('p', {}, 
        `Salary: ${sanitizedJob.salary || 'Not specified'}`);
    const jobType = createSafeElement('p', {}, 
        `Type: ${sanitizedJob.job_type}`);
    
    details.appendChild(techStack);
    details.appendChild(location);
    details.appendChild(salary);
    details.appendChild(jobType);
    
    const actions = createSafeElement('div', {
        className: 'mt-4 flex space-x-4'
    });
    
    const viewLink = createSafeElement('a', {
        href: sanitizedJob.source_url,
        className: 'text-blue-600 hover:underline',
        target: '_blank'
    }, 'View Job');
    
    const saveButton = createSafeElement('button', {
        className: 'text-green-600 hover:underline'
    }, 'Save Job');
    
    actions.appendChild(viewLink);
    actions.appendChild(saveButton);
    
    card.appendChild(header);
    card.appendChild(details);
    card.appendChild(actions);
    
    return card;
}

// Export functions for use in other files
window.SecurityUtils = {
    escapeHtml: escapeHtml,
    sanitizeJobData: sanitizeJobData,
    createSafeElement: createSafeElement,
    createSafeJobCard: createSafeJobCard
};
