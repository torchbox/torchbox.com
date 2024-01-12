# Note: This file is loaded on all environments, even production.

alias dj="python manage.py"

if [ "$BUILD_ENV" = "dev" ]; then
    alias djrun="python manage.py runserver 0.0.0.0:8000"
    alias djtest="python manage.py test --settings=tbx.settings.test"
    alias djcov="coverage erase && \
                coverage run --branch manage.py test --settings=tbx.settings.test && \
                coverage report --skip-covered --skip-empty --show-missing"
fi

# nvm
if [ -a "$HOME/.nvm/nvm.sh" ]; then
  export NVM_DIR="$HOME/.nvm"
  source "$NVM_DIR/nvm.sh"
fi

alias honcho="honcho -f docker/Procfile"
