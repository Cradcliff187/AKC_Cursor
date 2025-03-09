# Construction CRM

A comprehensive Customer Relationship Management (CRM) system tailored for construction companies. This application helps manage customers, projects, time tracking, materials, and more.

## Features

- **Customer Management**: Track customer information, contact details, and project history
- **Project Management**: Create and manage projects with status transitions and financial summaries
- **Time Tracking**: Log employee hours with detailed reports and filtering
- **Materials Management**: Track material costs, receipts, and vendor information
- **Financial Tracking**: Monitor project costs, labor, materials, and overall profitability

## Technology Stack

- **Frontend**: Next.js with TypeScript, Tailwind CSS
- **Backend**: Supabase (PostgreSQL database)
- **Authentication**: Supabase Auth

## Getting Started

### Prerequisites

- Node.js (v14.0.0 or later)
- npm (v6.0.0 or later)

### Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd construction-crm
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file in the root directory with your Supabase credentials:
```
NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

- `/app` - Next.js application pages and routes
- `/components` - Reusable UI components
- `/lib` - Utility functions and constants
- `/database` - SQL scripts for database setup

## License

[MIT](LICENSE) 