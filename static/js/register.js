document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMsg = document.getElementById('errorMsg');
    const errorText = document.getElementById('errorText');
    const successMsg = document.getElementById('successMsg');

    // Form fields
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const fullName = document.getElementById('full_name');
    const terms = document.getElementById('terms');

    // Validation elements
    const usernameError = document.getElementById('username-error');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const termsError = document.getElementById('terms-error');

    // Icons
    const usernameIcon = document.getElementById('username-icon');
    const emailIcon = document.getElementById('email-icon');
    const passwordIcon = document.getElementById('password-icon');

    // Password strength
    const passwordStrength = document.getElementById('password-strength');

    let isSubmitting = false;

    // Real-time validation
    username.addEventListener('input', validateUsername);
    email.addEventListener('input', validateEmail);
    password.addEventListener('input', validatePassword);
    terms.addEventListener('change', validateTerms);

    // Form submission
    form.addEventListener('submit', handleSubmit);

    function validateUsername() {
        const value = username.value.trim();
        const isValid = value.length >= 3 && value.length <= 50 && /^[a-zA-Z0-9_]+$/.test(value);

        updateFieldValidation(username, usernameError, usernameIcon, isValid,
            'Username must be 3-50 characters (letters, numbers, underscore only)');
        return isValid;
    }

    function validateEmail() {
        const value = email.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(value);

        updateFieldValidation(email, emailError, emailIcon, isValid,
            'Please enter a valid email address');
        return isValid;
    }

    function validatePassword() {
        const value = password.value;
        let strength = 0;

        if (value.length >= 6) strength++;
        if (value.length >= 8) strength++;
        if (/[A-Z]/.test(value)) strength++;
        if (/[a-z]/.test(value)) strength++;
        if (/[0-9]/.test(value)) strength++;
        if (/[^A-Za-z0-9]/.test(value)) strength++;

        // Update password strength indicator
        passwordStrength.className = 'password-strength';
        if (value.length > 0) {
            if (strength < 3) {
                passwordStrength.classList.add('strength-weak');
            } else if (strength < 5) {
                passwordStrength.classList.add('strength-medium');
            } else {
                passwordStrength.classList.add('strength-strong');
            }
        }

        const isValid = value.length >= 6;
        updateFieldValidation(password, passwordError, null, isValid,
            'Password must be at least 6 characters');
        return isValid;
    }

    function validateTerms() {
        const isValid = terms.checked;
        updateFieldValidation(null, termsError, null, isValid,
            'You must agree to the terms');
        return isValid;
    }

    function updateFieldValidation(input, errorElement, iconElement, isValid, errorMessage) {
        if (isValid) {
            if (input) input.classList.remove('border-red-500');
            if (input) input.classList.add('border-green-500');
            if (errorElement) errorElement.classList.remove('show');
            if (iconElement) {
                iconElement.className = 'fas fa-check-circle success-icon';
                iconElement.classList.remove('hidden');
            }
        } else {
            if (input) input.classList.remove('border-green-500');
            if (input) input.classList.add('border-red-500');
            if (errorElement) {
                errorElement.textContent = errorMessage;
                errorElement.classList.add('show');
            }
            if (iconElement) {
                iconElement.className = 'fas fa-exclamation-circle error-icon';
                iconElement.classList.remove('hidden');
            }
        }
    }

    function togglePassword() {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        passwordIcon.className = type === 'password' ? 'fas fa-eye toggle-password cursor-pointer' : 'fas fa-eye-slash toggle-password cursor-pointer';
    }

    // Make togglePassword function global
    window.togglePassword = togglePassword;

    async function handleSubmit(e) {
        e.preventDefault();

        if (isSubmitting) return;

        // Validate all fields
        const isUsernameValid = validateUsername();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        const isTermsValid = validateTerms();

        if (!isUsernameValid || !isEmailValid || !isPasswordValid || !isTermsValid) {
            showError('Please correct the errors above');
            return;
        }

        // Start loading state
        setLoadingState(true);
        hideMessages();

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username.value.trim(),
                    email: email.value.trim(),
                    password: password.value,
                    full_name: fullName.value.trim()
                })
            });

            const data = await response.json();

            if (response.ok) {
                showSuccess();
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showError(data.detail || 'Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showError('Network error. Please check your connection and try again.');
        } finally {
            setLoadingState(false);
        }
    }

    function setLoadingState(loading) {
        isSubmitting = loading;
        submitBtn.disabled = loading;

        if (loading) {
            btnText.textContent = 'Creating Account...';
            loadingSpinner.classList.remove('hidden');
            submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
        } else {
            btnText.textContent = 'Create Account';
            loadingSpinner.classList.add('hidden');
            submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    }

    function showError(message) {
        errorText.textContent = message;
        errorMsg.classList.remove('hidden');
        successMsg.classList.add('hidden');
    }

    function showSuccess() {
        successMsg.classList.remove('hidden');
        errorMsg.classList.add('hidden');
    }

    function hideMessages() {
        errorMsg.classList.add('hidden');
        successMsg.classList.add('hidden');
    }

    // Add smooth scrolling for error messages
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe form groups for animation
    document.querySelectorAll('.form-group').forEach(group => {
        observer.observe(group);
    });

    // Add keyboard navigation improvements
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {
            e.preventDefault();
            const form = e.target.form;
            const index = Array.prototype.indexOf.call(form, e.target);
            const nextElement = form.elements[index + 1];

            if (nextElement) {
                nextElement.focus();
            } else {
                form.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Add focus/blur effects
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});
