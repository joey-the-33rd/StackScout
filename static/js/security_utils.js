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
 * Deep sanitizes job data including nested objects and arrays
 * @param {object} job - The job object to sanitize
 * @returns {object} - Sanitized job object with all strings escaped
 */
function sanitizeJobData(job) {
    if (typeof job === 'string') {
        return escapeHtml(job);
    }
    
    if (Array.isArray(job)) {
        return job.map(item => sanitizeJobData(item));
    }
    
    if (job !== null && typeof job === 'object') {
        const sanitized = {};
        for (const [key, value] of Object.entries(job)) {
            sanitized[key] = sanitizeJobData(value);
        }
        return sanitized;
    }
    
    return job;
}

/**
 * Validates if a URL is safe to use as href
 * @param {string} url - The URL to validate
 * @returns {boolean} - True if URL is safe
 */
function isSafeUrl(url) {
    if (typeof url !== 'string') {
        return false;
    }
    
    try {
        const parsedUrl = new URL(url);
        const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
        return allowedProtocols.includes(parsedUrl.protocol.toLowerCase());
    } catch (e) {
        // If URL parsing fails, it's likely a relative URL or malformed
        // Allow relative URLs but block javascript: and data: schemes
        const lowerUrl = url.toLowerCase().trim();
        return !lowerUrl.startsWith('javascript:') && 
               !lowerUrl.startsWith('data:') && 
               !lowerUrl.startsWith('vbscript:') &&
               !lowerUrl.startsWith('file:');
    }
}

/**
 * Whitelist of safe HTML attributes
 */
const SAFE_ATTRIBUTES = new Set([
    'class', 'className', 'id', 'href', 'src', 'alt', 'title', 'type',
    'value', 'placeholder', 'disabled', 'readonly', 'checked', 'selected',
    'data-', 'aria-', 'role', 'tabindex', 'style', 'target', 'rel',
    'width', 'height', 'maxlength', 'minlength', 'pattern', 'required'
]);

/**
 * Checks if an attribute name is safe
 * @param {string} attrName - The attribute name to check
 * @returns {boolean} - True if attribute is safe
 */
function isSafeAttribute(attrName) {
    if (typeof attrName !== 'string') {
        return false;
    }
    
    const lowerAttr = attrName.toLowerCase();
    
    // Block all event handlers (on*)
    if (lowerAttr.startsWith('on')) {
        return false;
    }
    
    // Block dangerous attributes
    const dangerousAttrs = new Set([
        'javascript:', 'vbscript:', 'data:', 'expression(', 'behavior',
        'binding', 'dynsrc', 'lowsrc', 'srcdoc', 'formaction'
    ]);
    
    for (const dangerous of dangerousAttrs) {
        if (lowerAttr.includes(dangerous)) {
            return false;
        }
    }
    
    // Check against whitelist
    for (const safe of SAFE_ATTRIBUTES) {
        if (safe.endsWith('-')) {
            if (lowerAttr.startsWith(safe)) {
                return true;
            }
        } else if (lowerAttr === safe) {
            return true;
        }
    }
    
    return false;
}

/**
 * Creates a safe DOM element with sanitized content and validated attributes
 * @param {string} tagName - The HTML tag name
 * @param {object} attributes - Element attributes (will be validated)
 * @param {string} textContent - Text content (will be escaped)
 * @returns {HTMLElement} - Safe DOM element
 */
function createSafeElement(tagName, attributes = {}, textContent = '') {
    const element = document.createElement(tagName);
    
    for (const [key, value] of Object.entries(attributes)) {
        if (isSafeAttribute(key)) {
            // Special handling for href attributes
            if (key.toLowerCase() === 'href' && !isSafeUrl(value)) {
                console.warn(`Blocked unsafe URL: ${value}`);
                continue;
            }
            
            // Special handling for src attributes
            if (key.toLowerCase() === 'src' && !isSafeUrl(value)) {
                console.warn(`Blocked unsafe src URL: ${value}`);
                continue;
            }
            
            element.setAttribute(key, value);
        } else {
            console.warn(`Blocked unsafe attribute: ${key}`);
        }
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
        target: '_blank',
        rel: 'noopener noreferrer'
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
    createSafeJobCard: createSafeJobCard,
    isSafeUrl: isSafeUrl,
    isSafeAttribute: isSafeAttribute
};
