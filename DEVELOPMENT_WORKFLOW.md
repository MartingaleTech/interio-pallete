# Development Workflow Guide

This document explains how to work on Interio Palette as an ongoing project.

## 📂 Project Structure

```
interio-pallete/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── main.py       # Main application file (all endpoints)
│   │   └── __init__.py
│   ├── pyproject.toml    # Python dependencies
│   └── poetry.lock
├── frontend/             # React frontend
│   ├── src/
│   │   ├── App.tsx       # Main application component
│   │   ├── components/   # UI components (shadcn/ui)
│   │   └── ...
│   ├── package.json      # Node dependencies
│   └── .env              # Environment variables
├── README.md             # Setup and usage guide
├── PROJECT_STATUS.md     # Current status and tracking
└── DEVELOPMENT_WORKFLOW.md  # This file
```

## 🔄 Development Cycle

### 1. Pick a Task
- Check `PROJECT_STATUS.md` for TODO items
- Choose from HIGH, MEDIUM, or LOW priority
- Update status to "IN PROGRESS"

### 2. Make Changes
- Work on backend or frontend as needed
- Test locally as you go
- Follow existing code patterns

### 3. Test
**Backend:**
```bash
cd backend
poetry run fastapi dev app/main.py
# Test at http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm run dev
# Test at http://localhost:5173
```

### 4. Commit Changes
```bash
git add <files>
git commit -m "feat: descriptive commit message"
git push origin initial-implementation
```

### 5. Update Documentation
- Mark task as complete in `PROJECT_STATUS.md`
- Update README if needed
- Add notes about new features

## 🎯 Common Tasks

### Adding a New UI Form

1. **Check if API endpoint exists** in `backend/app/main.py`
2. **Add form state** in `frontend/src/App.tsx`
3. **Create form UI** using existing patterns
4. **Connect to API** with fetch
5. **Test the flow**

**Example Pattern:**
```typescript
const [showAddForm, setShowAddForm] = useState(false)
const [formData, setFormData] = useState({ /* fields */ })

const handleSubmit = async () => {
  const res = await fetch(`${API_URL}/api/endpoint`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(formData)
  })
  if (res.ok) {
    // Success handling
    fetchData() // Refresh list
  }
}
```

### Adding a New API Endpoint

1. **Define Pydantic model** (if needed) in `backend/app/main.py`
2. **Add endpoint function**
3. **Add proper authentication/authorization**
4. **Test with curl or API docs**

**Example Pattern:**
```python
@app.post("/api/endpoint", response_model=ResponseModel)
async def create_thing(data: CreateModel, user: User = Depends(get_current_user)):
    # Validate user has access
    if user.org_id != data.org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create and store
    thing_id = str(uuid.uuid4())
    new_thing = Thing(id=thing_id, **data.model_dump())
    things_db[thing_id] = new_thing
    
    return new_thing
```

### Migrating to PostgreSQL

When ready to add real database:

1. **Install dependencies:**
```bash
cd backend
poetry add sqlalchemy psycopg2-binary alembic
```

2. **Create models file** `backend/app/models.py`
3. **Replace dictionary operations** with SQLAlchemy queries
4. **Set up migrations** with Alembic
5. **Update README** with database setup instructions

## 📝 Commit Message Convention

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add client creation form in organization dashboard
fix: resolve phone OTP validation error
docs: update README with PostgreSQL setup
refactor: extract API client into separate file
```

## 🔍 Testing Checklist

Before committing:
- [ ] Backend starts without errors
- [ ] Frontend builds without errors
- [ ] New feature works as expected
- [ ] Existing features still work
- [ ] No console errors in browser
- [ ] Responsive on mobile (if UI change)

## 🐛 Debugging Tips

### Backend Issues
```bash
# Check logs in terminal where backend is running
# API docs: http://localhost:8000/docs
# Test endpoints with curl or Postman
```

### Frontend Issues
```bash
# Check browser console (F12)
# Check Network tab for API calls
# Use React DevTools
```

### Common Issues
1. **CORS errors**: Backend CORS is configured, but check API_URL in frontend .env
2. **401 Unauthorized**: Token might be expired, log out and log back in
3. **Module not found**: Run `npm install` or `poetry install`

## 📊 Tracking Progress

### Update PROJECT_STATUS.md regularly:
```markdown
## 🚧 IN PROGRESS
- [ ] Adding client creation form - 50% complete

## ✅ COMPLETED FEATURES
- [x] Client creation form with validation
```

### Keep KNOWN ISSUES updated:
```markdown
## 🐛 KNOWN ISSUES
3. Form validation doesn't show error for invalid email
```

## 🎨 Code Style Guidelines

### Backend (Python)
- Follow PEP 8
- Use type hints
- Keep functions focused and small
- Use Pydantic for validation

### Frontend (TypeScript)
- Use TypeScript interfaces
- Keep components under 300 lines
- Extract reusable logic into hooks
- Use Tailwind CSS for styling (no custom CSS unless necessary)

## 🔐 Security Reminders

- Never commit `.env` files with real credentials
- Always validate user input
- Check user permissions before operations
- Hash passwords (already implemented with bcrypt)
- Use HTTPS in production

## 🚀 When Ready for Production

1. Set up PostgreSQL database
2. Configure real SMS provider
3. Set up cloud file storage
4. Configure production environment variables
5. Set up monitoring (Sentry, etc.)
6. Deploy backend (Fly.io, Railway, etc.)
7. Deploy frontend (Vercel, Netlify, etc.)
8. Set up domain and SSL
9. Configure backup strategy

## 🤝 Getting Help

### If stuck on something:
1. Check this workflow guide
2. Check README.md for setup issues
3. Check PROJECT_STATUS.md for context
4. Review existing code for patterns
5. Test with API docs at `/docs`
6. Ask specific questions with context

### Useful Resources:
- FastAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/
- shadcn/ui: https://ui.shadcn.com/
- Tailwind CSS: https://tailwindcss.com/

## 📞 Session Handoff

When pausing work or handing off:

1. **Commit all changes**
2. **Update PROJECT_STATUS.md** with current state
3. **Note any blockers** or decisions needed
4. **List next steps** clearly
5. **Push to GitHub**

**Template:**
```markdown
## Last Session: [Date]
**What was done:**
- Implemented X feature
- Fixed Y bug

**Current state:**
- Feature X is 80% complete
- Waiting on decision about Y

**Next steps:**
- Complete form validation for X
- Test full workflow
- Update documentation

**Blockers:**
- Need to decide on SMS provider
```
