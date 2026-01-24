### Marketing Hub

Frappe Framework based Marketing App for managing marketing operations of an organization

**Features**:
- Campaign Management with budget tracking
- Content Management System with templates
- Lead Attribution (UTM tracking)
- Marketing Expense tracking with GL integration
- Omni-channel blasts (Email, WhatsApp, SMS)
- Social Media posting (framework ready)
- Analytics sync (framework ready)
- Agency mode for multi-client operations

**Integrations**:
- **ERPNext**: Email Settings, SMS Settings, Accounting (GL entries)
- **frappe_whatsapp**: WhatsApp Business API integration (optional)
- **CRM**: Lead attribution and tracking (optional)

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench --site your-site.local install-app marketing_hub
bench --site your-site.local migrate
```

**Full Setup Guide**: See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/marketing_hub
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
