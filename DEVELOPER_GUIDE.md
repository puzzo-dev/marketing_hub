# Marketing Hub - Developer Guide

## Setup & Installation

### Prerequisites
- Frappe Framework v15+
- Node.js 18+
- Redis

### Installation
```bash
bench get-app marketing_hub https://github.com/your-repo/marketing_hub
bench --site [site-name] install-app marketing_hub
```

### Local Development
1. **Start Bench**:
   ```bash
   bench start
   ```
2. **Watch Frontend** (Hot Reload):
   ```bash
   cd apps/marketing_hub
   yarn watch
   ```

## Project Structure
- `marketing_hub/`
  - `doctype/`: Python backend logic
  - `report/`: Script reports
  - `www/marketing/api.py`: Portal API endpoints
- `desk/`
  - `src/pages/`: Vue.js frontend pages
  - `src/components/`: Reusable Vue components

## Contributing

### Backend (Python)
- Use Type Hints where possible.
- Ensure all API methods are decorated with `@frappe.whitelist()`.
- Place complex logic in `utils/` rather than bloating doctype controllers.

### Frontend (Vue.js)
- Use **Frappe UI** components (`Button`, `FormControl`, `ListView`).
- Avoid custom CSS; use TailwindCSS classes.
- Use `createResource` for all API calls.

## Testing
- **Unit Tests**: Run `bench run-tests --app marketing_hub`.
- **Manual UI Testing**: Verify standard user flows (Create Campaign, Send Blast, Sync Analytics).

## API Documentation
See `www/marketing/api.py` for the definitive list of endpoints available to the frontend.
