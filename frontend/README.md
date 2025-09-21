# TaskPilot Frontend

React frontend for the TaskPilot task management application.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Hook Form** with Zod validation
- **Axios** for API communication

## Features

- ✅ User authentication (signup/login)
- ✅ Responsive design with Tailwind CSS
- ✅ Form validation with Zod schemas
- ✅ Protected routes
- ✅ Authentication context management
- ✅ Error handling and loading states

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### API Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` (the FastAPI backend). Make sure the backend is running on port 8000.

## Project Structure

```
src/
├── components/     # Reusable UI components
├── context/        # React context providers
├── pages/          # Page components
├── services/       # API service functions
├── types/          # TypeScript type definitions
├── App.tsx         # Main app component
└── main.tsx        # Entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## Authentication

The app uses JWT tokens for authentication with the following flow:

1. User signs up or logs in
2. JWT token is stored in localStorage
3. Token is included in API requests via Axios interceptors
4. Authentication state is managed via React Context
5. Routes are protected based on authentication status

