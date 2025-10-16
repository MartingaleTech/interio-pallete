# Testing Infrastructure

This directory contains test files for the application.

## Test Structure

- **Unit Tests**: Test individual components, hooks, and utilities
- **Integration Tests**: Test feature modules and their interactions
- **E2E Tests**: Test complete user workflows

## Running Tests

Currently, the project uses Vite's default testing setup. To add comprehensive testing:

1. Install testing dependencies:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

2. Add test script to package.json:
```json
"test": "vitest",
"test:ui": "vitest --ui",
"test:coverage": "vitest --coverage"
```

3. Create vitest.config.ts in the root directory

## Example Test Structure

```
tests/
├── unit/
│   ├── components/
│   ├── hooks/
│   └── utils/
├── integration/
│   ├── features/
│   └── services/
└── e2e/
    └── workflows/
```

## Writing Tests

Example component test:
```typescript
import { render, screen } from '@testing-library/react'
import { LoginForm } from '../features/auth/components/LoginForm'

describe('LoginForm', () => {
  it('renders phone input', () => {
    render(<LoginForm />)
    expect(screen.getByPlaceholderText(/phone number/i)).toBeInTheDocument()
  })
})
```

Example hook test:
```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { useProjects } from '../hooks/useProjects'

describe('useProjects', () => {
  it('fetches projects', async () => {
    const { result } = renderHook(() => useProjects('token'))
    await waitFor(() => expect(result.current.projects).toBeDefined())
  })
})
```
