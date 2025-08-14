import { Page, Locator } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

/**
 * Base Page Object Model for GENESIS Platform
 *
 * Provides common functionality and navigation patterns
 * shared across all pages in the application.
 */
export class BasePage {
  protected helpers: TestHelpers;

  // Common selectors used across pages
  protected selectors = {
    navigation: {
      sidebar: '[data-testid="sidebar"]',
      mobileMenuButton: '[data-testid="mobile-menu-button"]',
      userMenu: '[data-testid="user-menu"]',
      notifications: '[data-testid="notifications"]',
    },
    common: {
      loadingSpinner: '[data-testid="loading-spinner"]',
      errorMessage: '[data-testid="error-message"]',
      successMessage: '[data-testid="success-message"]',
      confirmDialog: '[data-testid="confirm-dialog"]',
      modalOverlay: '[data-testid="modal-overlay"]',
    },
    agents: {
      agentCard: '[data-testid="agent-card"]',
      agentStatus: '[data-testid="agent-status"]',
      agentSelector: '[data-testid="agent-selector"]',
    }
  };

  constructor(protected page: Page) {
    this.helpers = new TestHelpers(page);
  }

  /**
   * Navigate to specific page
   */
  async goto(path: string) {
    await this.page.goto(path);
    await this.waitForPageLoad();
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle', { timeout: 10000 });

    // Wait for any loading spinners to disappear
    await this.page.waitForSelector(this.selectors.common.loadingSpinner, {
      state: 'hidden',
      timeout: 5000
    }).catch(() => {
      // Loading spinner might not exist
    });
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      await this.page.waitForSelector(this.selectors.navigation.userMenu, {
        state: 'visible',
        timeout: 3000
      });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get current page title
   */
  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * Check for error messages on page
   */
  async hasErrorMessages(): Promise<boolean> {
    try {
      await this.page.waitForSelector(this.selectors.common.errorMessage, {
        state: 'visible',
        timeout: 1000
      });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string | null> {
    const hasError = await this.hasErrorMessages();
    if (!hasError) return null;

    const errorElement = this.page.locator(this.selectors.common.errorMessage);
    return await errorElement.textContent();
  }

  /**
   * Wait for success message
   */
  async waitForSuccessMessage(timeout: number = 5000): Promise<string> {
    const successElement = this.page.locator(this.selectors.common.successMessage);
    await successElement.waitFor({ state: 'visible', timeout });
    return (await successElement.textContent()) || '';
  }

  /**
   * Close any open modals
   */
  async closeModals() {
    const modal = this.page.locator(this.selectors.common.modalOverlay);
    const isVisible = await modal.isVisible();

    if (isVisible) {
      // Try to close via escape key first
      await this.page.keyboard.press('Escape');
      await this.page.waitForTimeout(500);

      // If still visible, try clicking overlay
      if (await modal.isVisible()) {
        await modal.click({ position: { x: 10, y: 10 } });
      }
    }
  }

  /**
   * Navigate using sidebar
   */
  async navigateViaSidebar(itemName: string) {
    // Ensure sidebar is visible (handle mobile)
    const sidebar = this.page.locator(this.selectors.navigation.sidebar);
    const isSidebarVisible = await sidebar.isVisible();

    if (!isSidebarVisible) {
      const mobileButton = this.page.locator(this.selectors.navigation.mobileMenuButton);
      if (await mobileButton.isVisible()) {
        await mobileButton.click();
        await sidebar.waitFor({ state: 'visible' });
      }
    }

    // Click navigation item
    const navItem = sidebar.locator(`text="${itemName}"`);
    await navItem.click();

    // Wait for navigation to complete
    await this.waitForPageLoad();
  }

  /**
   * Get available agents
   */
  async getAvailableAgents(): Promise<string[]> {
    const agentCards = this.page.locator(this.selectors.agents.agentCard);
    const count = await agentCards.count();
    const agents: string[] = [];

    for (let i = 0; i < count; i++) {
      const agentName = await agentCards.nth(i).getAttribute('data-agent-name');
      if (agentName) {
        agents.push(agentName);
      }
    }

    return agents;
  }

  /**
   * Select specific agent
   */
  async selectAgent(agentName: string) {
    const agentCard = this.page.locator(
      `${this.selectors.agents.agentCard}[data-agent-name="${agentName}"]`
    );
    await agentCard.click();

    // Wait for agent to be selected/loaded
    await this.page.waitForTimeout(1000);
  }

  /**
   * Check agent status
   */
  async getAgentStatus(agentName: string): Promise<string | null> {
    const agentCard = this.page.locator(
      `${this.selectors.agents.agentCard}[data-agent-name="${agentName}"]`
    );
    const statusElement = agentCard.locator(this.selectors.agents.agentStatus);

    try {
      return await statusElement.textContent();
    } catch {
      return null;
    }
  }

  /**
   * Logout user
   */
  async logout() {
    const userMenu = this.page.locator(this.selectors.navigation.userMenu);
    await userMenu.click();

    const logoutButton = this.page.locator('[data-testid="logout-button"]');
    await logoutButton.click();

    // Wait for redirect to login page
    await this.page.waitForURL('**/signin');
  }

  /**
   * Take screenshot for current page
   */
  async takeScreenshot(name?: string): Promise<string> {
    const pageName = name || (await this.getPageTitle()).toLowerCase().replace(/\s+/g, '-');
    return await this.helpers.takeContextualScreenshot(pageName, true);
  }

  /**
   * Validate page accessibility (basic checks)
   */
  async validateAccessibility(): Promise<{ issues: string[] }> {
    const issues: string[] = [];

    // Check for proper heading structure
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').all();
    if (headings.length === 0) {
      issues.push('No heading elements found');
    }

    // Check for alt text on images
    const images = await this.page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      if (!alt) {
        issues.push('Image without alt text found');
        break; // Only report once per page
      }
    }

    // Check for proper form labels
    const inputs = await this.page.locator('input').all();
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');

      if (id) {
        const label = await this.page.locator(`label[for="${id}"]`).count();
        if (label === 0 && !ariaLabel) {
          issues.push('Input without proper labeling found');
          break;
        }
      } else if (!ariaLabel) {
        issues.push('Input without id or aria-label found');
        break;
      }
    }

    return { issues };
  }

  /**
   * Monitor page performance
   */
  async getPerformanceMetrics() {
    return await this.helpers.validatePagePerformance();
  }

  /**
   * Wait for specific network request
   */
  async waitForNetworkRequest(urlPattern: string | RegExp, timeout: number = 10000) {
    const pattern = typeof urlPattern === 'string' ? new RegExp(urlPattern) : urlPattern;

    return new Promise<any>((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.page.off('response', responseHandler);
        reject(new Error(`Network request timeout: ${urlPattern}`));
      }, timeout);

      const responseHandler = (response: any) => {
        if (pattern.test(response.url())) {
          clearTimeout(timeoutId);
          this.page.off('response', responseHandler);
          resolve(response);
        }
      };

      this.page.on('response', responseHandler);
    });
  }
}
