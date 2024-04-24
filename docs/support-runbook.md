# Support runbook

This document describes possible ways in which the system may fail or malfunction, with instructions how to handle and recover from these scenarios.

This runbook is supplementary to the [general 24/7 support runbook](https://intranet.torchbox.com/propositions/design-and-build-proposition/delivering-projects/dedicated-support-team/247-support-out-of-hours-runbook/), with details about project-specific actions which may be necessary for troubleshooting and restoring service.

See also our [incident process](https://intranet.torchbox.com/propositions/design-and-build-proposition/delivering-projects/application-support/incident-process/) if you're not already following this.

## Support resources

###Project resources

- [Project repository](https://github.com/torchbox/torchbox.com)
- [Monday.com project](https://torchbox.monday.com/boards/1192293412/)
- [Production site](https://torchbox-com-production.torchbox.dev/)
- [Staging site](https://torchbox-com-staging.torchbox.dev/)
- Developers slack: `#torchbox-website-dev`
- Editors ('client') slack: `#torchbox-website-editors`

###Monitoring

- [Papertrail production](https://my.papertrailapp.com/systems/torchbox-com-production/events)
- [Papertrail staging](https://my.papertrailapp.com/systems/torchbox-com-staging/events)
- [Sentry project](https://torchbox.sentry.io/projects/torchbox-website/?project=1221893)
- [Scout APM](https://scoutapm.com/apps/371126)

###Infrastructure

- S3 bucket production: `buckup-torchbox-production-new` (Note that there is a ticket to change this post-launch)
- S3 bucket staging: `buckup-torchbox-staging-new`
- [Heroku Production](https://dashboard.heroku.com/apps/torchbox-com-production)
- [Heroku Staging](https://dashboard.heroku.com/apps/torchbox-com-staging)

###Documentation

- See [External documentation](/external-docs)

## Scenarios

The build is a simple wagtail build, with no external integrations, and no donation flow. For now there are no obvious points of failure to document.
