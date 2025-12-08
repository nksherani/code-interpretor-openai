# Contributing to OpenAI Code Interpreter Explorer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (OS, Python version, Node version, etc.)

**Bug Report Template:**

```markdown
### Description
[Clear description of the bug]

### Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Environment
- OS: [e.g., Windows 11, macOS 13]
- Python: [e.g., 3.11.5]
- Node.js: [e.g., 18.17.0]
- Browser: [e.g., Chrome 120]

### Screenshots
[If applicable]

### Additional Context
[Any other relevant information]
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear title** describing the enhancement
- **Provide detailed description** of the suggested enhancement
- **Explain why** this enhancement would be useful
- **Provide examples** of how it would be used

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Write clear commit messages**
6. **Submit the pull request**

## Development Setup

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions.

Quick setup:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Maximum line length: 100 characters

**Example:**

```python
from typing import Optional, List

def process_data(data: List[dict], filter_key: Optional[str] = None) -> List[dict]:
    """
    Process and filter data based on provided key.
    
    Args:
        data: List of dictionaries to process
        filter_key: Optional key to filter by
        
    Returns:
        Filtered list of dictionaries
    """
    if filter_key:
        return [item for item in data if filter_key in item]
    return data
```

### JavaScript/React (Frontend)

- Use ES6+ syntax
- Follow functional component patterns
- Use PropTypes or TypeScript for type checking
- Maximum line length: 100 characters
- Use meaningful variable names

**Example:**

```javascript
// Good
const UserProfile = ({ username, email, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  
  const handleSave = async () => {
    // Implementation
  };
  
  return (
    <div className="user-profile">
      {/* JSX */}
    </div>
  );
};

// Bad
const UP = ({ u, e, f }) => {
  const [x, setX] = useState(false);
  return <div>{u}</div>;
};
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**

```
feat: add file upload progress indicator
fix: resolve issue with file download on Safari
docs: update API documentation for new endpoints
refactor: simplify data processing logic in analyzer
```

## Project Structure

```
openai-code-interpretor/
├── backend/              # FastAPI backend
│   ├── main.py          # Main API application
│   ├── requirements.txt # Python dependencies
│   └── tests/           # Backend tests (if added)
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── utils/       # Utility functions
│   │   └── App.jsx      # Main app component
│   └── package.json     # Node dependencies
└── docs/               # Additional documentation
```

## Testing

### Backend Tests

We use `pytest` for backend testing:

```bash
cd backend
pytest
```

### Frontend Tests

We use Jest and React Testing Library:

```bash
cd frontend
npm test
```

### Writing Tests

**Backend Test Example:**

```python
def test_analyze_data():
    request = AnalysisRequest(
        prompt="Test prompt",
        file_ids=[]
    )
    response = analyze_data(request)
    assert response.thread_id is not None
    assert isinstance(response.message, str)
```

**Frontend Test Example:**

```javascript
import { render, screen } from '@testing-library/react';
import ChatInterface from './ChatInterface';

test('renders chat interface', () => {
  render(<ChatInterface />);
  const inputElement = screen.getByPlaceholderText(/ask me anything/i);
  expect(inputElement).toBeInTheDocument();
});
```

## Documentation

### Code Comments

- Explain **why**, not **what** the code does
- Use comments for complex logic
- Keep comments up-to-date with code changes

### API Documentation

- Update API_DOCUMENTATION.md for any API changes
- Include request/response examples
- Document error cases

### README Updates

- Update README.md if you add new features
- Keep installation instructions current
- Update screenshots if UI changes significantly

## Feature Requests

We welcome feature requests! To suggest a feature:

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with the `enhancement` label
3. **Describe the feature** in detail
4. **Explain the use case** and benefits
5. **Provide examples** if applicable

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update README.md** if needed
5. **Request review** from maintainers

### PR Template

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
[Describe how you tested the changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings
```

## Getting Help

If you need help:

1. **Check documentation** (README, SETUP_GUIDE, API_DOCUMENTATION)
2. **Search existing issues**
3. **Ask in discussions** section
4. **Create a new issue** with the `question` label

## Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

Feel free to reach out by creating an issue with the `question` label.

Thank you for contributing! 🎉

