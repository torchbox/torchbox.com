from django.core.exceptions import ValidationError
from django.utils.functional import cached_property

from wagtail.models import Page, Site

from tbx.core.models import BasePage


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
    """

    template = "patterns/pages/sitemap/sitemap_page.html"

    parent_page_types = ["torchbox.HomePage"]
    subpage_types = []
    max_count = 1

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
          - 'section': the top-level Page, with .title and .url
          - 'pages':   nested list of {"page": ..., "children": [...]} nodes

        Request-scoped caching:
          `@cached_property` is safe here. In Wagtail, Page.serve() fetches a
          fresh page instance from the database per HTTP request, so this cache
          is scoped to a single request-response cycle.

        Query strategy (single query, O(n) assembly):
          One path-filtered query fetches all live, public pages at or below
          section depth. Pages are indexed by Treebeard path; each page's parent
          is found in O(1) by slicing path[:-Page.steplen]. Pages whose parent
          is not in the index are top-level sections (their parent is the
          homepage, which is excluded from the query by depth filter).
        """
        try:
            site = Site.objects.get(is_default_site=True)
        except (Site.DoesNotExist, Site.MultipleObjectsReturned):
            # Fail closed on misconfigured installs — empty sitemap beats 500.
            return []

        root = site.root_page

        # Fetch all live, public pages from section depth downward.
        # path__startswith scopes to this site's tree without assuming depth.
        # depth__gte=root.depth+1 skips root itself; the homepage (root.depth)
        # is deliberately absent so section pages fall into the else branch below.
        # Exclusions (see class docstring for reasoning):
        #   - .live().public()          — unpublished + password-protected pages
        #   - .exclude(slug='incident') — mirrors base.html noindex rule
        #   - .not_type(SitemapPage)    — /sitemap/ must not list itself
        pages = list(
            Page.objects.filter(
                path__startswith=root.path,
                depth__gte=root.depth + 1,
            )
            .live()
            .public()
            .exclude(slug="incident")
            .not_type(SitemapPage)
            .order_by("path")
            .defer_streamfields()
        )

        # Index nodes by path for O(1) parent lookup.
        # Insertion order is path order, so parents always precede children.
        nodes = {page.path: {"page": page, "children": []} for page in pages}

        sections = []
        for path, node in nodes.items():
            parent_path = path[: -Page.steplen]
            if parent_path in nodes:
                nodes[parent_path]["children"].append(node)
            else:
                # Parent not in index → this page's parent is the homepage.
                sections.append({"section": node["page"], "pages": node["children"]})

        return sections

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["sections"] = self.sections
        return context
