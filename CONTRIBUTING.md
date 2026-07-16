# Contributing

Thanks for considering a contribution to PricePulse.

## Local workflow
1. Fork the repository.
2. Create a feature branch from `main`.
3. Run the backend and frontend locally.
4. Run the validation steps before opening a PR.

## Setup
### Backend
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Frontend
```bash
cd frontend1/frontend
npm install
npm run dev
```

## Validation
```bash
cd backend
python manage.py check --settings=config.test_settings
python manage.py test --settings=config.test_settings

cd ../frontend1/frontend
npm run lint
npm run build
```

## Guidelines
- Do not rewrite the provider architecture.
- Do not remove `FakeProvider`.
- Prefer focused fixes over broad refactors.
- Keep API changes backward-compatible.
- Add tests when touching auth, permissions, serializers, or provider matching.
- Document any anti-bot/provider limitations honestly in code comments and PRs.

## Pull requests
- Explain the user-visible impact.
- Call out migrations and environment variable changes.
- Include screenshots for UI changes when relevant.
- Include a short test plan.