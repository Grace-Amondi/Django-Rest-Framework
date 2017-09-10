from snippets.models import Snippet,Location
from snippets.serializers import SnippetSerializer
from snippets.serializers import UserSerializer
from snippets.serializers import LocationSerializer
# from snippets.serializers imporr NetworkGeoSerializer
from rest_framework import generics
from rest_framework import permissions
from django.contrib.auth.models import User
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework_gis.filters import DistanceToPointFilter


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LocationList(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    distance_filter_field = 'geometry'
    filter_backends = (DistanceToPointFilter, )
    bbox_filter_include_overlapping = True # Optional


