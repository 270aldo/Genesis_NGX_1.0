/**
 * Logger utility for GENESIS SDK
 */

export class Logger {
  private enabled: boolean
  private prefix: string

  constructor(enabled: boolean = false, prefix: string = '[GENESIS SDK]') {
    this.enabled = enabled
    this.prefix = prefix
  }

  debug(...args: any[]) {
    if (this.enabled) {
      console.debug(this.prefix, ...args)
    }
  }

  info(...args: any[]) {
    if (this.enabled) {
      console.info(this.prefix, ...args)
    }
  }

  warn(...args: any[]) {
    console.warn(this.prefix, ...args)
  }

  error(...args: any[]) {
    console.error(this.prefix, ...args)
  }

  setEnabled(enabled: boolean) {
    this.enabled = enabled
  }

  setPrefix(prefix: string) {
    this.prefix = prefix
  }
}