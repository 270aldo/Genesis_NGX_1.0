import { Page, expect } from '@playwright/test';
import { BasePage } from './base-page';

/**
 * Authentication Page Object Model
 *
 * Handles login, signup, password reset and authentication-related
 * functionality for the GENESIS platform.
 */
export class AuthPage extends BasePage {
  private readonly selectors = {
    signin: {
      emailInput: '[data-testid="email-input"]',
      passwordInput: '[data-testid="password-input"]',
      signinButton: '[data-testid="signin-button"]',
      forgotPasswordLink: '[data-testid="forgot-password-link"]',
      signupLink: '[data-testid="signup-link"]',
      rememberMeCheckbox: '[data-testid="remember-me"]',
    },
    signup: {
      firstNameInput: '[data-testid="first-name-input"]',
      lastNameInput: '[data-testid="last-name-input"]',
      emailInput: '[data-testid="email-input"]',
      passwordInput: '[data-testid="password-input"]',
      confirmPasswordInput: '[data-testid="confirm-password-input"]',
      signupButton: '[data-testid="signup-button"]',
      signinLink: '[data-testid="signin-link"]',
      termsCheckbox: '[data-testid="terms-checkbox"]',
    },
    forgotPassword: {
      emailInput: '[data-testid="email-input"]',
      sendResetButton: '[data-testid="send-reset-button"]',
      backToSigninLink: '[data-testid="back-to-signin"]',
    },
    common: {
      errorMessage: '[data-testid="auth-error"]',
      successMessage: '[data-testid="auth-success"]',
      loadingSpinner: '[data-testid="auth-loading"]',
    }
  };

  constructor(page: Page) {
    super(page);
  }

  // Navigation Methods
  async goToSignin() {
    await this.goto('/signin');
    await this.waitForAuthPage();
  }

  async goToSignup() {
    await this.goto('/signup');
    await this.waitForAuthPage();
  }

  async goToForgotPassword() {
    await this.goto('/forgot-password');
    await this.waitForAuthPage();
  }

  private async waitForAuthPage() {
    await this.page.waitForSelector('form', { state: 'visible' });
    await this.helpers.waitForNetworkIdle();
  }

  // Sign In Methods
  async signin(email: string, password: string, rememberMe: boolean = false) {
    await this.fillSigninForm(email, password, rememberMe);
    await this.submitSigninForm();
    await this.waitForAuthenticationComplete();
  }

  async fillSigninForm(email: string, password: string, rememberMe: boolean = false) {
    await this.helpers.humanType(this.selectors.signin.emailInput, email);
    await this.helpers.humanType(this.selectors.signin.passwordInput, password);

    if (rememberMe) {
      await this.helpers.humanClick(this.selectors.signin.rememberMeCheckbox);
    }
  }

  async submitSigninForm() {
    await this.helpers.humanClick(this.selectors.signin.signinButton);
  }

  async waitForAuthenticationComplete(timeout: number = 10000) {
    // Wait for loading to complete
    await this.page.waitForSelector(this.selectors.common.loadingSpinner, {
      state: 'hidden',
      timeout: 5000
    }).catch(() => {
      // Loading spinner might not appear for cached responses
    });

    // Wait for successful redirect or error message
    try {
      await Promise.race([
        this.page.waitForURL('**/dashboard', { timeout }),
        this.page.waitForSelector(this.selectors.common.errorMessage, {
          state: 'visible',
          timeout
        })
      ]);
    } catch (error) {
      throw new Error(`Authentication did not complete within ${timeout}ms`);
    }
  }

  // Sign Up Methods
  async signup(userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
    acceptTerms?: boolean;
  }) {
    await this.fillSignupForm(userData);
    await this.submitSignupForm();
    await this.waitForSignupComplete();
  }

  async fillSignupForm(userData: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
    acceptTerms?: boolean;
  }) {
    await this.helpers.humanType(this.selectors.signup.firstNameInput, userData.firstName);
    await this.helpers.humanType(this.selectors.signup.lastNameInput, userData.lastName);
    await this.helpers.humanType(this.selectors.signup.emailInput, userData.email);
    await this.helpers.humanType(this.selectors.signup.passwordInput, userData.password);
    await this.helpers.humanType(this.selectors.signup.confirmPasswordInput, userData.confirmPassword);

    if (userData.acceptTerms !== false) {
      await this.helpers.humanClick(this.selectors.signup.termsCheckbox);
    }
  }

  async submitSignupForm() {
    await this.helpers.humanClick(this.selectors.signup.signupButton);
  }

  async waitForSignupComplete(timeout: number = 15000) {
    // Wait for loading to complete
    await this.page.waitForSelector(this.selectors.common.loadingSpinner, {
      state: 'hidden',
      timeout: 5000
    }).catch(() => {
      // Loading spinner might not appear
    });

    // Wait for success message or error
    try {
      await Promise.race([
        this.page.waitForSelector(this.selectors.common.successMessage, {
          state: 'visible',
          timeout
        }),
        this.page.waitForSelector(this.selectors.common.errorMessage, {
          state: 'visible',
          timeout
        }),
        this.page.waitForURL('**/dashboard', { timeout }) // Auto-signin after signup
      ]);
    } catch (error) {
      throw new Error(`Signup did not complete within ${timeout}ms`);
    }
  }

  // Password Reset Methods
  async requestPasswordReset(email: string) {
    await this.helpers.humanType(this.selectors.forgotPassword.emailInput, email);
    await this.helpers.humanClick(this.selectors.forgotPassword.sendResetButton);
    await this.waitForPasswordResetSent();
  }

  async waitForPasswordResetSent(timeout: number = 10000) {
    await this.page.waitForSelector(this.selectors.common.successMessage, {
      state: 'visible',
      timeout
    });
  }

  // Navigation Between Auth Pages
  async goToSignupFromSignin() {
    await this.helpers.humanClick(this.selectors.signin.signupLink);
    await this.waitForAuthPage();
  }

  async goToSigninFromSignup() {
    await this.helpers.humanClick(this.selectors.signup.signinLink);
    await this.waitForAuthPage();
  }

  async goToForgotPasswordFromSignin() {
    await this.helpers.humanClick(this.selectors.signin.forgotPasswordLink);
    await this.waitForAuthPage();
  }

  async goToSigninFromForgotPassword() {
    await this.helpers.humanClick(this.selectors.forgotPassword.backToSigninLink);
    await this.waitForAuthPage();
  }

  // Validation Methods
  async getAuthError(): Promise<string | null> {
    try {
      const errorElement = this.page.locator(this.selectors.common.errorMessage);
      await errorElement.waitFor({ state: 'visible', timeout: 3000 });
      return await errorElement.textContent();
    } catch {
      return null;
    }
  }

  async getAuthSuccess(): Promise<string | null> {
    try {
      const successElement = this.page.locator(this.selectors.common.successMessage);
      await successElement.waitFor({ state: 'visible', timeout: 3000 });
      return await successElement.textContent();
    } catch {
      return null;
    }
  }

  async isSigninFormValid(): Promise<boolean> {
    const emailFilled = await this.page.locator(this.selectors.signin.emailInput).inputValue();
    const passwordFilled = await this.page.locator(this.selectors.signin.passwordInput).inputValue();
    const buttonEnabled = await this.page.locator(this.selectors.signin.signinButton).isEnabled();

    return emailFilled.length > 0 && passwordFilled.length > 0 && buttonEnabled;
  }

  async isSignupFormValid(): Promise<boolean> {
    const firstName = await this.page.locator(this.selectors.signup.firstNameInput).inputValue();
    const lastName = await this.page.locator(this.selectors.signup.lastNameInput).inputValue();
    const email = await this.page.locator(this.selectors.signup.emailInput).inputValue();
    const password = await this.page.locator(this.selectors.signup.passwordInput).inputValue();
    const confirmPassword = await this.page.locator(this.selectors.signup.confirmPasswordInput).inputValue();
    const termsAccepted = await this.page.locator(this.selectors.signup.termsCheckbox).isChecked();
    const buttonEnabled = await this.page.locator(this.selectors.signup.signupButton).isEnabled();

    return (
      firstName.length > 0 &&
      lastName.length > 0 &&
      email.length > 0 &&
      password.length > 0 &&
      confirmPassword.length > 0 &&
      password === confirmPassword &&
      termsAccepted &&
      buttonEnabled
    );
  }

  // Test Helper Methods
  async attemptInvalidLogin(email: string, password: string) {
    await this.fillSigninForm(email, password);
    await this.submitSigninForm();

    // Should stay on signin page with error
    await this.page.waitForSelector(this.selectors.common.errorMessage, {
      state: 'visible',
      timeout: 10000
    });
  }

  async testPasswordStrength(password: string): Promise<{
    strength: string;
    requirements: { [key: string]: boolean };
  }> {
    // Navigate to signup if not already there
    const currentUrl = this.page.url();
    if (!currentUrl.includes('signup')) {
      await this.goToSignup();
    }

    // Type password and check strength indicator
    await this.helpers.humanType(this.selectors.signup.passwordInput, password);

    // Wait for password strength calculation
    await this.page.waitForTimeout(500);

    // Extract password strength feedback (if available)
    const strengthIndicator = this.page.locator('[data-testid="password-strength"]');
    let strength = 'unknown';

    try {
      strength = await strengthIndicator.textContent() || 'unknown';
    } catch {
      // No strength indicator available
    }

    // Check basic password requirements
    const requirements = {
      minLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumbers: /\d/.test(password),
      hasSpecialChars: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    return { strength, requirements };
  }

  // Session Management
  async clearAuthenticationState() {
    // Clear localStorage and sessionStorage
    await this.page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Clear cookies
    await this.page.context().clearCookies();
  }

  async verifyAuthenticationPersistence() {
    // Reload page and check if still authenticated
    await this.page.reload();
    await this.waitForPageLoad();

    return await this.isAuthenticated();
  }
}
