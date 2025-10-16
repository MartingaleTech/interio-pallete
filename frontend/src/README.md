# Frontend Application Structure

This document describes the new modular architecture of the frontend application.

## Directory Structure

```
src/
├── features/              # Feature-based modules
│   ├── auth/             # Authentication feature
│   │   └── components/   # Auth-specific components
│   ├── admin/            # Admin dashboard feature
│   │   └── components/   # Admin-specific components
│   ├── organization/     # Organization dashboard feature
│   │   └── components/   # Organization-specific components
│   │       └── tabs/     # Tab components
│   └── client/           # Client dashboard feature
│       └── components/   # Client-specific components
├── state/                # Global state management
│   └── AuthContext.tsx   # Authentication context
├── services/             # API service layer
│   ├── api.ts           # Base API utilities
│   ├── authService.ts   # Auth API calls
│   ├── adminService.ts  # Admin API calls
│   ├── organizationService.ts # Org API calls
│   └── clientService.ts # Client API calls
├── hooks/                # Custom React hooks
│   ├── useProjects.ts   # Projects data hook
│   └── useClients.ts    # Clients data hook
├── types/                # TypeScript type definitions
│   └── index.ts         # All shared types
├── components/           # Shared/reusable components
│   ├── ui/              # UI library components (shadcn)
│   └── shared/          # Custom shared components
├── utils/                # Utility functions
├── tests/                # Test files
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── App.tsx              # Main app component
└── main.tsx             # App entry point

## Key Principles

### 1. Feature-Based Organization
Each major feature (auth, admin, organization, client) has its own directory with:
- Components specific to that feature
- Feature-specific hooks (if needed)
- Feature-specific types (if needed)

### 2. Separation of Concerns
- **Services**: Handle all API communication
- **State**: Manage global application state
- **Hooks**: Encapsulate reusable logic
- **Components**: Focus on UI rendering

### 3. Type Safety
All shared types are defined in `types/index.ts` for consistency across the app.

### 4. Reusability
Shared components like `DashboardHeader` are placed in `components/shared/` for use across features.

## How to Add New Features

1. Create a new feature directory under `features/`
2. Add components specific to that feature
3. Create service methods in the appropriate service file
4. Define types in `types/index.ts`
5. Create custom hooks if needed
6. Wire up the feature in `App.tsx`

## State Management

The app uses React Context API for global state:
- `AuthContext`: Manages user authentication state

To add new global state:
1. Create a new context in `state/`
2. Provide it in `App.tsx` or a parent component
3. Consume it using the `useContext` hook

## API Services

All API calls go through the service layer:
- Centralized error handling
- Consistent request/response formatting
- Easy to mock for testing
- Type-safe with TypeScript

## Testing

Tests are organized by type:
- **Unit tests**: Test individual functions, hooks, and components
- **Integration tests**: Test feature modules together
- **E2E tests**: Test complete user workflows

See `tests/README.md` for more details on testing.

## Component Guidelines

1. Keep components focused on a single responsibility
2. Extract complex logic into custom hooks
3. Use TypeScript for all components
4. Prefer functional components with hooks
5. Use shared types from `types/index.ts`
6. Keep components small and composable
