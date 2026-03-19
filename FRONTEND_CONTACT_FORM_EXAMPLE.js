/**
 * Messaging Integration - Frontend Example
 * 
 * This shows how to update your contact form to support multi-channel messaging:
 * - Email (SendGrid)
 * - WhatsApp (Twilio)
 * - SMS (Twilio)
 * 
 * The contact form now allows users to choose which channels to use.
 */

// ============================================================================
// HTML Form Example (add to contact.html)
// ============================================================================

const contactFormHTML = `
<form id="contact-form" class="form">
  <!-- Name -->
  <div class="form-group">
    <label for="contact-name">Name *</label>
    <input 
      type="text" 
      id="contact-name" 
      name="name" 
      required 
      placeholder="Your name"
    />
  </div>

  <!-- Email -->
  <div class="form-group">
    <label for="contact-email">Email *</label>
    <input 
      type="email" 
      id="contact-email" 
      name="email" 
      required 
      placeholder="your@email.com"
    />
  </div>

  <!-- Phone (optional, required for WhatsApp/SMS) -->
  <div class="form-group">
    <label for="contact-phone">Phone (optional)</label>
    <input 
      type="tel" 
      id="contact-phone" 
      name="phone" 
      placeholder="+1 (555) 123-4567"
      title="Format: +1234567890 (include country code)"
    />
  </div>

  <!-- Message -->
  <div class="form-group">
    <label for="contact-message">Message *</label>
    <textarea 
      id="contact-message" 
      name="message" 
      required 
      placeholder="Your message..."
      rows="5"
    ></textarea>
  </div>

  <!-- Messaging Channels Selection -->
  <div class="form-group">
    <label>How should we contact you? *</label>
    <div class="checkbox-group">
      <label class="checkbox-label">
        <input 
          type="checkbox" 
          name="channel" 
          value="email" 
          checked 
          id="channel-email"
        />
        <span>📧 Email</span>
      </label>
      <label class="checkbox-label">
        <input 
          type="checkbox" 
          name="channel" 
          value="whatsapp" 
          id="channel-whatsapp"
        />
        <span>💬 WhatsApp</span>
        <small>(requires phone number)</small>
      </label>
      <label class="checkbox-label">
        <input 
          type="checkbox" 
          name="channel" 
          value="sms" 
          id="channel-sms"
        />
        <span>📱 SMS</span>
        <small>(requires phone number)</small>
      </label>
    </div>
    <small class="form-hint">
      ⚠️ WhatsApp & SMS require a phone number in format: +1234567890
    </small>
  </div>

  <!-- reCAPTCHA -->
  <div class="g-recaptcha" data-sitekey="${window.RECAPTCHA_SITE_KEY}"></div>

  <!-- Submit Button -->
  <button type="submit" class="btn btn-primary">Send Message</button>
</form>
`;

// ============================================================================
// JavaScript Handler (add to scripts/main.js or contact-form.js)
// ============================================================================

class ContactFormHandler {
  constructor(formId = 'contact-form') {
    this.form = document.getElementById(formId);
    if (!this.form) {
      console.error(`Form with ID "${formId}" not found`);
      return;
    }
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Update phone requirement based on channel selection
    const channelCheckboxes = document.querySelectorAll('input[name="channel"]');
    const phoneInput = document.getElementById('contact-phone');

    channelCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        const needsPhone =
          document.getElementById('channel-whatsapp')?.checked ||
          document.getElementById('channel-sms')?.checked;

        if (needsPhone) {
          phoneInput.setAttribute('required', 'required');
          phoneInput.classList.add('required');
        } else {
          phoneInput.removeAttribute('required');
          phoneInput.classList.remove('required');
        }
      });
    });

    // Handle form submission
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }

  validatePhoneNumber(phone) {
    // Phone format: +1234567890
    const phoneRegex = /^\+[1-9]\d{1,14}$/;
    return phoneRegex.test(phone);
  }

  getSelectedChannels() {
    const checkboxes = document.querySelectorAll(
      'input[name="channel"]:checked'
    );
    return Array.from(checkboxes).map(cb => cb.value);
  }

  async handleSubmit(event) {
    event.preventDefault();

    // Get form data
    const name = document.getElementById('contact-name').value.trim();
    const email = document.getElementById('contact-email').value.trim();
    const phone = document.getElementById('contact-phone').value.trim();
    const message = document.getElementById('contact-message').value.trim();
    const channels = this.getSelectedChannels();

    // Validate
    if (!name || !email || !message) {
      this.showError('Please fill in all required fields');
      return;
    }

    if (!channels.length) {
      this.showError('Please select at least one contact method');
      return;
    }

    // Validate phone if WhatsApp or SMS selected
    if ((channels.includes('whatsapp') || channels.includes('sms')) && phone) {
      if (!this.validatePhoneNumber(phone)) {
        this.showError('Phone number must be in format: +1234567890');
        return;
      }
    } else if (channels.includes('whatsapp') || channels.includes('sms')) {
      this.showError('Phone number required for WhatsApp or SMS');
      return;
    }

    // Get reCAPTCHA token
    let recaptchaToken;
    try {
      recaptchaToken = await this.getRecaptchaToken();
    } catch (error) {
      this.showError('reCAPTCHA verification failed');
      return;
    }

    // Submit form
    await this.submitContactForm({
      name,
      email,
      phone,
      message,
      channels,
      recaptcha_token: recaptchaToken,
    });
  }

  async getRecaptchaToken() {
    return new Promise((resolve, reject) => {
      if (typeof grecaptcha === 'undefined') {
        reject(new Error('reCAPTCHA not loaded'));
        return;
      }
      grecaptcha.ready(() => {
        grecaptcha
          .execute(window.RECAPTCHA_SITE_KEY, { action: 'submit' })
          .then(resolve)
          .catch(reject);
      });
    });
  }

  async submitContactForm(data) {
    const submitBtn = this.form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';

      const response = await fetch(`${window.API_BASE}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to send message');
      }

      // Success!
      this.showSuccess(
        `Message sent successfully via: ${data.channels.join(', ')}`
      );
      this.form.reset();

      // Log channel-specific results (for debugging)
      console.log('Contact form results:', result.channels);

    } catch (error) {
      console.error('Contact form error:', error);
      this.showError(error.message || 'Failed to send message. Please try again.');

    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  }

  showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success';
    alertDiv.textContent = '✅ ' + message;
    alertDiv.style.cssText = 'margin-bottom: 1rem; padding: 1rem; background-color: #d4edda; color: #155724; border-radius: 0.25rem;';
    this.form.parentElement.insertBefore(alertDiv, this.form);
    setTimeout(() => alertDiv.remove(), 5000);
  }

  showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-error';
    alertDiv.textContent = '❌ ' + message;
    alertDiv.style.cssText = 'margin-bottom: 1rem; padding: 1rem; background-color: #f8d7da; color: #721c24; border-radius: 0.25rem;';
    this.form.parentElement.insertBefore(alertDiv, this.form);
    setTimeout(() => alertDiv.remove(), 5000);
  }
}

// ============================================================================
// Initialize on Page Load
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Make sure API_BASE is configured
  if (typeof window.API_BASE === 'undefined') {
    console.error('window.API_BASE is not defined. Check config/env.js');
    return;
  }

  // Initialize contact form handler
  new ContactFormHandler('contact-form');
});

// ============================================================================
// CSS Styling (add to styles/global.css)
// ============================================================================

const styles = `
/* Contact Form */
.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  font: inherit;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-light);
}

.form-group input[required]:valid {
  border-color: #28a745;
}

/* Checkbox Group */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}

.checkbox-label small {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-left: 0.25rem;
}

/* Form Hints */
.form-hint {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* Alert Messages */
.alert {
  padding: 1rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border-left: 4px solid #28a745;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border-left: 4px solid #dc3545;
}

/* Submit Button */
.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: var(--accent);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--accent-dark);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
`;

// ============================================================================
// Testing the Contact Form
// ============================================================================

const testContactForm = {
  // Test with email only
  async testEmailOnly() {
    const payload = {
      name: 'Test User',
      email: 'test@example.com',
      phone: '',
      message: 'This is a test message via email only.',
      channels: ['email'],
      recaptcha_token: 'test-token',
    };

    const response = await fetch(`${window.API_BASE}/api/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    console.log('Email Test:', await response.json());
  },

  // Test with multiple channels
  async testMultiChannel() {
    const payload = {
      name: 'Test User',
      email: 'test@example.com',
      phone: '+1234567890',
      message: 'Testing all channels!',
      channels: ['email', 'whatsapp', 'sms'],
      recaptcha_token: 'test-token',
    };

    const response = await fetch(`${window.API_BASE}/api/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    console.log('Multi-Channel Test:', await response.json());
  },
};

// Run tests: testContactForm.testEmailOnly()
