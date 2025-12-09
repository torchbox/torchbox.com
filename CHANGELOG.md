# Changelog

All notable changes to this project will be documented in this file. This project doesn’t follow any versioning scheme.

Add your changes to the Unreleased section and move them to the appropriate section when they are merged.

## Unreleased

- Several upgrades via [#412](https://github.com/torchbox/torchbox.com/pull/412)
  - Wagtail 7.1 → 7.2
  - Node.js 20 → 24
  - **Build & Infrastructure**:
    - Major Webpack ecosystem upgrade (Webpack 5.103+, CLI 6+, Dev Server 5+)
    - TypeScript upgrade (4.9 → 5.9)
    - Sass upgrade (1.95) with deprecation fixes and relative path refactoring
    - Stylelint upgrade (v13 → v16) and Prettier upgrade (v2 → v3)
    - Removed `clean-webpack-plugin` (replaced by native Webpack 5 functionality)
    - Added `django-upgrade` and `pyupgrade`
    - Updated `copy-webpack-plugin`, `mini-css-extract-plugin`, `eslint-webpack-plugin`
    - Updated loaders: `ts-loader`, `url-loader`, `css-loader`, `sass-loader`, `postcss-loader`
    - Updated PostCSS ecosystem: `postcss`, `autoprefixer`, `cssnano`, `postcss-custom-properties`
  - **Python Dependencies**:
    - Django ecosystem: `django-debug-toolbar` (6.1), `django-redis` (6.0), `redis` (7.1), `django-phonenumber-field` (8.4), `django-permissions-policy`
    - Wagtail ecosystem: `wagtail-markdown`, `wagtailmedia`
    - Monitoring: `sentry-sdk` (2.47), `scout-apm` (3.5)
    - AWS: `boto3`/`botocore` (1.42), `s3transfer` (0.16)
    - Utilities: `whitenoise` (6.11), `psycopg` (3.3), `beautifulsoup4`, `urllib3`, `Faker`, `phonenumbers`, `tblib`, `Werkzeug`
    - Tooling: `ruff` (0.14), `pre-commit`, `pudb`, `djhtml`
    - Documentation: `mkdocs-material` (9.7), `pymdown-extensions`
  - **Node Dependencies**:
    - Jest upgrade (v29 → v30)
    - Swiper upgrade (v11 → v12)
    - `cssnano` upgrade (v6 → v7)
    - `lite-youtube-embed` update

## 2025-09-00

- Wagtail 7.1 upgrade [#404]https://github.com/torchbox/torchbox.com/pull/404

## 2025-06-23

- Wagtail 7.0 upgrade [#396](https://github.com/torchbox/torchbox.com/pull/396)

---

## 2025 (pre-changelog 04-06-2025)

This changelog was started on 04-06-2025. Before that date, changes were not documented here.
