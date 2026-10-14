import os

from django.core.management.base import BaseCommand, CommandError

from wagtail.contrib.redirects.models import Redirect


TORCHBOX_DOMAIN = "https://torchbox.com"


class Command(BaseCommand):
    help = "Find Wagtail redirects that point to a torchbox.com URL"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the matching redirects instead of just listing them",
        )

    def handle(self, *args, **options):
        sentry_env = os.environ.get("SENTRY_ENVIRONMENT", "")
        if sentry_env == "production":
            raise CommandError(
                "This command cannot be run in the production environment."
            )

        qs = Redirect.objects.filter(redirect_link__icontains=TORCHBOX_DOMAIN)
        matches = list(qs.values_list("old_path", "redirect_link"))

        if not matches:
            self.stdout.write("No redirects pointing to torchbox.com were found.")
            return

        self.stdout.write(
            f"Found {len(matches)} redirect(s) pointing to torchbox.com:\n"
        )
        for old_path, redirect_link in matches:
            self.stdout.write(f"  {old_path}  →  {redirect_link}")

        if options["delete"]:
            qs.delete()
            self.stdout.write(self.style.SUCCESS("\nDeleted redirects:"))
            for old_path, redirect_link in matches:
                self.stdout.write(
                    self.style.SUCCESS(f"  {old_path}  →  {redirect_link}")
                )
            self.stdout.write(self.style.SUCCESS(f"\nTotal deleted: {len(matches)}"))
