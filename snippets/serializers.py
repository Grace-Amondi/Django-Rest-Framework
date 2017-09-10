from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES, Location, Link
from django.contrib.auth.models import User
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'title', 'code', 'linenos', 'language', 'style', 'owner', 'highlight')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'snippets')


class LocationSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Location
        geo_field = "point"
        auto_bbox = True

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('id', 'name', 'recieved', 'county')


class NetworkGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Link
        geo_field = 'geo'
        auto_bbox = True

    def get_properties(self, instance, fields):
        # This is a PostgreSQL HStore field, which django maps to a dict
        return instance.metadata

    def unformat_geojson(self, feature):
        attrs = {
            self.Meta.geo_field: feature["geometry"],
            "metadata": feature["properties"]
        }

        if self.Meta.bbox_geo_field and "bbox" in feature:
            attrs[self.Meta.bbox_geo_field] = Polygon.from_bbox(feature["bbox"])

        return attrs
