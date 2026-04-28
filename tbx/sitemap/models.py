from django.core.exceptions import ValidationError
from django.utils.functional import cached_property

from wagtail.models import Page, Site

from tbx.core.models import BasePage


def _build_tree(pages):
    """
    Convert a flat, path-ordered list of pages into a nested tree.
    Each node is {"page": <Page>, "children": [...]}.
    Pages must be ordered by treebeard path so ancestors always appear
    before their descendants.
    """
    root = []
    stack = []  # [(node, absolute_depth)]
    for page in pages:
        node = {"page": page, "children": []}
        depth = page.depth
        while stack and stack[-1][1] >= depth:
            stack.pop()
        if stack:
            stack[-1][0]["children"].append(node)
        else:
            root.append(node)
        stack.append((node, depth))
    return root


class SitemapPage(BasePage):
    """
    A Wagtail page that renders all live, public pages grouped by top-level
    section. Content is generated programmatically from the page tree — editors
    control only the slug and standard page metadata.

    Exclusion logic mirrors wagtail.contrib.sitemaps: `.live().public()` filters
    unpublished and password-protected pages. Pages with slug='incident' are also
    excluded — that slug is the site's per-page noindex mechanism (see
    tbx/project_styleguide/templates/patterns/base.html for the canonical noindex
    rule). BasePage has no custom noindex field, so this slug check is the only
    per-page exclusion required.

    The /search/ path is disallowed in robots.txt but maps to a Django view
    (tbx/core/views.py), not a Wagtail page, so it cannot appear in the tree
    and requires no explicit filter.
    """

    template = "patterns/pages/sitemap/sitemap_page.html"

    # SitemapPage should only ever be created once, under the site root.
    parent_page_types = ["wagtailcore.Page", "torchbox.HomePage"]
    # No child pages allowed — this is a terminal content page.
    subpage_types = []

    class Meta:
        verbose_name = "Sitemap page"

    def clean(self):
        super().clean()
        self.slug = "sitemap"
        if SitemapPage.objects.exclude(pk=self.pk).exists():
            raise ValidationError("A Sitemap page already exists. Only one is allowed.")

    @cached_property
    def sections(self):
        """
        Return a list of dicts, one per top-level section under the site root.
        Each dict has:
          - 'section': the top-level Page (specific), with .title and .url
          - 'pages':   list of live, public descendant pages (specific),
                       ordered by path (tree order), NOT including the section
                       root itself (the section heading renders it separately).

        Request-scoped caching:
          `@cached_property` is safe here. In Wagtail, Page.serve() fetches a
          fresh page instance from the database per HTTP request, so this cache
          is scoped to a single request-response cycle. The next request after
          a CMS publish/unpublish sees a new instance and re-runs this method
          against the updated tree.

        Query strategy (constant-query count, avoids N+1):
          1 query for top-level children (with `.exclude(slug='incident')`).
          1 query for ALL descendants of the site root (inclusive=False),
          filtered by live/public, excluding slug='incident' recursively (path
          prefix match), grouped in Python into per-section buckets.
        """
        try:
            site = Site.objects.get(is_default_site=True)
        except (Site.DoesNotExist, Site.MultipleObjectsReturned):
            # Fail closed on misconfigured installs — empty sitemap beats 500.
            return []

        root = site.root_page

        # Step 1: top-level sections (one query).
        # Exclusions (see class docstring for reasoning):
        #   - .live().public()     — unpublished + password-protected pages
        #   - .exclude(slug='incident') — mirrors base.html noindex rule
        #   - exclude SitemapPage itself so /sitemap/ doesn't appear as its
        #     own section heading
        top_level = (
            root.get_children()
            .live()
            .public()
            .exclude(slug="incident")
            .order_by("path")
            .specific()
        )
        sections_list = [p for p in top_level if not isinstance(p, SitemapPage)]
        if not sections_list:
            return []

        # Step 2: all descendants below the site root in one query, then group
        # by top-level ancestor in Python. `descendant_of(root)` uses a single
        # indexed path-range scan (treebeard/MPTT). defer_streamfields() avoids
        # loading StreamField payloads we never render.
        all_descendants = (
            Page.objects.descendant_of(root, inclusive=False)
            .live()
            .public()
            .exclude(slug="incident")
            .order_by("path")
            .defer_streamfields()
        )

        # Build a lookup: section.path -> list of pages whose path starts with
        # that section's path but is not equal to it (i.e. strict descendants).
        buckets = {section.path: [] for section in sections_list}
        section_paths = sorted(buckets.keys(), key=len, reverse=True)
        for descendant in all_descendants:
            for section_path in section_paths:
                # Treebeard paths are fixed-width segments; a strict descendant
                # has a path that STARTS WITH the ancestor path and is longer.
                if (
                    descendant.path.startswith(section_path)
                    and descendant.path != section_path
                ):
                    buckets[section_path].append(descendant)
                    break

        return [
            {"section": section, "pages": _build_tree(buckets[section.path])}
            for section in sections_list
        ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["sections"] = self.sections
        return context
