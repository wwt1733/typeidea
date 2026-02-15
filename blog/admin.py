# blog/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from blog.adminforms import PostAdminForm
from typeidea.custom_site import custom_site
from typeidea.base_admin import BaseOwnerAdmin
from blog.models import Tag, Category, Post
from django.contrib.admin.models import LogEntry

class PostInline(admin.TabularInline):
    # 在分类的增加页面中可以对文章进行编辑
    fields = ('title', 'desc')  # 定义了在内联表单中要显示的字段（对文章中的标题和摘要进行编辑）
    extra = 1   # 控制额外多几个
    model = Post   # 与Post关联


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline]
    list_display = ('name', 'status', 'is_nav', 'owner', 'created_time', 'post_count')  # 页面上显示的字段
    fields = ('name', 'status', 'is_nav')  # 增加时显示的字段

    def save_model(self, request, obj, form, change):
        obj.owner = request.user  # 当前已经登录的用户作为作者
        return super().save_model(request, obj, form, change)

    def post_count(self, obj):
        """ 统计文章数量 """
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'owner', 'created_time')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super().save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):
    """ 自定义过滤器只展示当前用户分类 """

    title = '分类过滤器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        # print(Category.objects.filter(owner=request.user).values_list('id', 'name'))
        # <QuerySet [(5, 'wdq'), (6, 'wwww')]>  打印下来的格式
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        # print(self.value())
        # 6          (显示id)
        category_id = self.value()
        if category_id:
            return queryset.filter(category__id=category_id)
        return queryset

# 新增代码如下！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = ['title', 'category', 'status', 'created_time', 'owner', 'operator']
    list_display_links = []
    list_filter = [CategoryOwnerFilter]

    search_fields = ['title', 'category_name']

    actions_on_top = True
    actions_on_bottom = False

    # 编辑页面
    save_on_top = True

    exclude = ('owner',)  # 必须这么写，因为The value of 'exclude' must be a list or tuple.

    fields = (
        ('category', 'title'),
        'desc',
        'status',
        'content',
        'tag',
    )

    def operator(self, obj):
        """ 新增编辑按钮 """
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=[obj.id])  # 修改地方！！！！！
        )

    operator.short_description = '操作'


    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(owner=request.user)

@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
