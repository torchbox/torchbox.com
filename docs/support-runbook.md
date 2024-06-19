# Support runbook

This document describes possible ways in which the system may fail or malfunction, with instructions how to handle and recover from these scenarios.

This runbook is supplementary to the [general 24/7 support runbook](https://intranet.torchbox.com/propositions/design-and-build-proposition/delivering-projects/dedicated-support-team/247-support-out-of-hours-runbook/), with details about project-specific actions which may be necessary for troubleshooting and restoring service.

See also our [incident process](https://intranet.torchbox.com/propositions/design-and-build-proposition/delivering-projects/application-support/incident-process/) if you're not already following this.

## Support resources

###Project resources

- [Project repository](https://github.com/torchbox/torchbox.com)
- [Monday.com project](https://torchbox.monday.com/boards/1192293412/)
- [Production site](https://torchbox.com/)
- [Staging site](https://torchbox-com-staging.torchbox.dev/)
- Developers slack: `#torchbox-website-dev`
- Editors ('client') slack: `#torchbox-website-editors`

###Monitoring

- [Papertrail production](https://my.papertrailapp.com/systems/torchbox-com-production/events)
- [Papertrail staging](https://my.papertrailapp.com/systems/torchbox-com-staging/events)
- [Sentry project](https://torchbox.sentry.io/projects/torchbox-website/?project=1221893)
- [Scout APM](https://scoutapm.com/apps/371126)

###Infrastructure

- S3 bucket production: `media.torchbox.com`
- S3 bucket staging: `buckup-torchbox-staging-new`
- [Heroku Production](https://dashboard.heroku.com/apps/torchbox-com-production)
- [Heroku Staging](https://dashboard.heroku.com/apps/torchbox-com-staging)

Note that the production site uses 1 professionals dyno rather than 2 standard dynos, in order to avoid memory issues due to image processing.

###Documentation

- See [External documentation](/external-docs)

## Scenarios

The build is a simple wagtail build, with no external integrations, and no donation flow.

## Scenario A: Server memory overload due to image processing

During the build we have experienced memory issues on the server due to:

- webp conversion of images
- large numbers of image renditions on some pages, due to using `{% srcset_image %}` and `<picture>` tags.

### 1. Has the whole server failed, or just one page that has run out of memory?

**If the whole site is down, and papertrail reports "Memory quota vastly exceeded", the site can generally be restarted in heroku.**

Visit https://dashboard.heroku.com/apps/torchbox-com-production, click on "More" and choose "Restart all dynos".

### 2. If only one page has thrown an error (typically it can occur in the editor's preview, when new image-heavy pages are being created)

- Usually it will recover
- If an editor has raised this as a problem:
  **The issue can temporarily be averted by asking the editor to hide the preview panel while making their changes**
- If the problem persists, investigate the size of the image they are using.

### 3. If a listing page has crashed because the image renditions have been re-created

**Leave it for a while. The server will continue to recreate the renditions in the background. In five minutes it will probably have recovered.**

Note that as part of mitigating this issue, we have run a script and all images in the bucket have been automatically resized if:

- they have more than 10,000,000px
- they are larger than 2mb

Also note that editors can no longer upload images that exceed these parameters
