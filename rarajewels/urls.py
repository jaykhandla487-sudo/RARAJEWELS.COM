"""
URL configuration for rarajewels project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url
from django.views.static import serve

# Sitemap
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import ProductSitemap, CategorySitemap

# Sitemap Dictionary
sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
}

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=static_url("images/favicon.ico"),
            permanent=True,
        ),
    ),

    # Sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("shop.urls")),
]

# Static Files
urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)

# Media Files
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
else:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]