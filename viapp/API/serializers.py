from rest_framework import serializers
from viapp.models import Album, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"


class AlbumSerializer(serializers.ModelSerializer):
    photos_count = serializers.SerializerMethodField()
    photos_ids = serializers.SerializerMethodField()
    
    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "owner",
            "shared_with",
            "photos_count",
            "photos_ids",
        ]

    def get_photos_count(self, obj):
        return obj.photos.count()

    def get_photos_ids(self, obj):
        return list(obj.photos.values_list("id", flat=True))