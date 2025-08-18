from rest_framework import serializers
from .models import (
    Tag, Category, Attachment, Comment, Dashboard, Widget,
    MenuItem, FAQ, Feedback, Announcement
)
from users.serializers import UserProfileSerializer


class TagSerializer(serializers.ModelSerializer):
    """
    Serializador para tags.
    """
    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializador para categorias.
    """
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para categorias, incluindo subcategorias.
    """
    parent = CategorySerializer(read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializador para anexos.
    """
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ('size', 'content_type', 'uploaded_at', 'uploaded_by')
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.user.first_name} {obj.uploaded_by.user.last_name}".strip() or obj.uploaded_by.user.username
        return None


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializador para comentários.
    """
    author_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.user.first_name} {obj.author.user.last_name}".strip() or obj.author.user.username
        return None
    
    def get_replies(self, obj):
        replies = obj.replies.filter(is_active=True)
        return CommentSerializer(replies, many=True).data


class WidgetSerializer(serializers.ModelSerializer):
    """
    Serializador para widgets.
    """
    class Meta:
        model = Widget
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializador para dashboards.
    """
    owner_name = serializers.SerializerMethodField()
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_owner_name(self, obj):
        if obj.owner:
            return f"{obj.owner.user.first_name} {obj.owner.user.last_name}".strip() or obj.owner.user.username
        return None
    
    def get_widgets_count(self, obj):
        return obj.widgets.count()


class DashboardDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para dashboards, incluindo widgets.
    """
    owner = UserProfileSerializer(read_only=True)
    widgets = WidgetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializador para itens de menu.
    """
    parent_title = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = '__all__'
    
    def get_parent_title(self, obj):
        return obj.parent.title if obj.parent else None


class MenuItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para itens de menu, incluindo subitens.
    """
    parent = MenuItemSerializer(read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = '__all__'
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order')
        return MenuItemSerializer(children, many=True).data


class FAQSerializer(serializers.ModelSerializer):
    """
    Serializador para FAQs.
    """
    category_name = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = FAQ
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_tags_list(self, obj):
        return [tag.name for tag in obj.tags.all()]


class FAQDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para FAQs.
    """
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    created_by = UserProfileSerializer(read_only=True)
    updated_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = FAQ
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializador para feedback.
    """
    user_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    feedback_type_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'resolved_at', 'created_by', 'updated_by')
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.user.first_name} {obj.user.user.last_name}".strip() or obj.user.user.username
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.user.first_name} {obj.assigned_to.user.last_name}".strip() or obj.assigned_to.user.username
        return None
    
    def get_feedback_type_display(self, obj):
        return dict(Feedback.FEEDBACK_TYPES)[obj.feedback_type]
    
    def get_priority_display(self, obj):
        return dict(Feedback.PRIORITY_LEVELS)[obj.priority]
    
    def get_status_display(self, obj):
        return dict(Feedback.STATUS_CHOICES)[obj.status]


class FeedbackDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para feedback.
    """
    user = UserProfileSerializer(read_only=True)
    assigned_to = UserProfileSerializer(read_only=True)
    created_by = UserProfileSerializer(read_only=True)
    updated_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'resolved_at')


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializador para anúncios.
    """
    is_current = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


class AnnouncementDetailSerializer(serializers.ModelSerializer):
    """
    Serializador detalhado para anúncios.
    """
    created_by = UserProfileSerializer(read_only=True)
    updated_by = UserProfileSerializer(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
