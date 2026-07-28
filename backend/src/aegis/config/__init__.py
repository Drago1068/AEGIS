"""Environment-driven application configuration.

This package owns reading configuration from environment variables via
``pydantic-settings``. No secrets, hostnames, or credentials are hardcoded anywhere in this
package or elsewhere in the codebase; every value has an environment-variable source and a
documented entry in ``.env.example`` / ``docs/operations/configuration.md``.
"""
