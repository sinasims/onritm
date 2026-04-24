from rest_framework import serializers
from shop.models import Singer, Track, Mood, Genre

class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['id', 'name_fa', 'name_en', 'slug']
        
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name_fa', 'name_en', 'slug']

class SingerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Singer
        fields = ['id', 'name_fa', 'name_en', 'slug', 'image', 'order']

class SingerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Singer
        fields = ['id', 'name_fa', 'name_en', 'slug', 'bio_fa', 'bio_en', 'image']

class TrackListSerializer(serializers.ModelSerializer):
    singer_name = serializers.CharField(source='singer.name_fa')
    cover_url = serializers.SerializerMethodField()
    sample_url = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ['id', 'title_fa', 'title_en', 'singer', 'singer_name', 'mood', 'genre', 'price', 'cover_url', 'sample_url', 'slug']

    def get_cover_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url  # چون عمومی است
        return None

    def get_sample_url(self, obj):
        if obj.sample_file:
            return obj.sample_file.url
        return None
    
class TrackDetailSerializer(serializers.ModelSerializer):
    singer = SingerDetailSerializer()
    mood = MoodSerializer()
    genre = GenreSerializer()

    class Meta:
        model = Track
        fields = ['id', 'title_fa', 'title_en', 'singer', 'mood', 'genre', 'price', 'cover_image', 'sample_file', 'instrumental_file', 'original_file', 'description_fa', 'description_en', 'created_at']