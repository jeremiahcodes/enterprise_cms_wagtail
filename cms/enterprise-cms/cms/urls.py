from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.static import serve
from django.contrib.auth.decorators import login_required
import os

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

# Custom view to serve private media files from Azure Storage
def serve_private_media(request, path):
    """
    Serve media files from Azure Storage with authentication.
    Only authenticated users (or superusers for admin) can access media files.
    """
    from django.core.files.storage import default_storage
    from django.http import HttpResponse, Http404
    from django.contrib.auth.decorators import user_passes_test
    
    # Check if user is authenticated (for Wagtail admin)
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    
    try:
        file = default_storage.open(path)
        # Get the file content
        content = file.read()
        file.close()
        
        # Determine content type
        import mimetypes
        content_type, _ = mimetypes.guess_type(path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        response = HttpResponse(content, content_type=content_type)
        return response
    except Exception:
        raise Http404("Media file not found")

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    # Serve private media files through Django
    path("media/<path:path>", serve_private_media, name="serve_private_media"),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# In production, media files are served through the serve_private_media view above

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
