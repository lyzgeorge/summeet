# Contributing to Summeet

Thank you for considering contributing to Summeet! We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Include details**: OS, browser, error messages, steps to reproduce
4. **Add logs** if available (remove any sensitive information)

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Describe the use case** and why it would be valuable
3. **Provide examples** of how the feature would work
4. **Consider implementation complexity** and alternatives

### Code Contributions

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/summeet.git
   cd summeet
   ```
3. **Set up development environment**:
   ```bash
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

#### Making Changes

1. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```

#### Code Standards

**Python (Backend)**
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Handle errors gracefully

**JavaScript/Vue (Frontend)**
- Use ES6+ features
- Follow Vue.js style guide
- Use meaningful component and variable names
- Keep components focused and reusable
- Handle loading/error states properly

**General**
- Write clear, self-documenting code
- Add comments for complex logic
- Keep commits atomic and focused
- Write meaningful commit messages

#### Testing

- **Backend**: Add tests for new API endpoints and functions
- **Frontend**: Test component functionality and user interactions
- **Integration**: Test end-to-end workflows when possible

#### Pull Request Process

1. **Update documentation** if needed
2. **Ensure tests pass** locally
3. **Create pull request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - List of changes made
4. **Address review feedback** promptly
5. **Keep PR focused** - one feature/fix per PR

## Development Setup

### Backend Development

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with API keys
cp ../env.example .env
# Edit .env with your API keys

# Run development server
python main.py
```

### Frontend Development

```bash
cd frontend
npm install

# Run development server
npm run dev
```

### Docker Development

```bash
# Build and run with Docker
docker compose -f docker-compose.simple.yml up --build
```

## Project Structure

```
summeet/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models.py           # Database models
│   ├── services.py         # AI services
│   └── requirements.txt    # Dependencies
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── App.vue        # Main component
│   │   └── api.js         # API client
│   └── package.json       # Dependencies
├── Dockerfile             # Single container build
└── docker-compose.simple.yml # Simple deployment
```

## Coding Guidelines

### API Design
- Follow RESTful conventions
- Use appropriate HTTP status codes
- Include proper error handling
- Document endpoints clearly

### Frontend Components
- Keep components small and focused
- Use props/events for communication
- Handle loading and error states
- Make components accessible

### Database
- Use descriptive column names
- Include appropriate indexes
- Handle migrations carefully
- Validate data at API level

## Security Considerations

- **Never commit API keys** or sensitive data
- **Validate all user inputs** on the backend
- **Handle file uploads safely** with size limits
- **Use HTTPS** in production
- **Keep dependencies updated**

## Documentation

- Update README.md for significant changes
- Document new API endpoints
- Add inline comments for complex logic
- Update environment variable examples

## Community

- Be respectful and inclusive
- Help others learn and contribute
- Provide constructive feedback
- Follow our Code of Conduct

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Request Comments**: For code-specific questions

Thank you for contributing to Summeet! 🎙️