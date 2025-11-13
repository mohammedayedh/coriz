from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging

from .models import Post, Category, Comment, Tag, ContactMessage, Newsletter, SiteSettings
from .forms import ContactForm, NewsletterForm
from authentication.models import User

logger = logging.getLogger(__name__)


def home_view(request):
    """الصفحة الرئيسية"""
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    featured_posts = Post.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-published_at')[:6]
    
    latest_posts = Post.objects.filter(
        status='published'
    ).order_by('-published_at')[:8]
    
    categories = Category.objects.filter(is_active=True).annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    popular_tags = Tag.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('-posts_count')[:10]
    
    context = {
        'site_settings': site_settings,
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'categories': categories,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'main/home.html', context)


def custom_page_not_found(request, exception=None):
    """عرض الصفحة المخصصة عند حدوث خطأ 404."""
    context = {
        'request_path': getattr(request, 'path', '/'),
    }
    return render(request, 'errors/404.html', context, status=404)


def posts_list_view(request):
    """قائمة المنشورات"""
    posts = Post.objects.filter(status='published').order_by('-published_at')
    
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        posts = posts.filter(category=category)
    else:
        category = None
    
    tag_slug = request.GET.get('tag')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)
    else:
        tag = None
    
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True).annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    tags = Tag.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'current_category': category,
        'current_tag': tag,
        'search_query': search_query,
    }
    
    return render(request, 'main/posts_list.html', context)


def post_detail_view(request, slug):
    """تفاصيل المنشور"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    related_posts = Post.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id).order_by('-published_at')[:4]
    
    comments = Comment.objects.filter(
        post=post,
        is_approved=True,
        parent=None
    ).order_by('-created_at')
    
    for comment in comments:
        comment.replies = Comment.objects.filter(
            parent=comment,
            is_approved=True
        ).order_by('created_at')
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
    }
    
    return render(request, 'main/post_detail.html', context)


@login_required
@require_http_methods(["POST"])
def add_comment_view(request, post_id):
    """إضافة تعليق"""
    post = get_object_or_404(Post, id=post_id, status='published')
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content:
            return JsonResponse({'success': False, 'message': 'محتوى التعليق مطلوب'})
        
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'التعليق الأب غير موجود'})
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent
        )
        
        post.comments_count += 1
        post.save(update_fields=['comments_count'])
        
        return JsonResponse({
            'success': True,
            'message': 'تم إضافة التعليق بنجاح',
            'comment_id': comment.id
        })
        
    except Exception as e:
        logger.error(f"خطأ في إضافة التعليق: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ أثناء إضافة التعليق'})


@require_http_methods(["GET", "POST"])
def contact_view(request):
    """صفحة التواصل"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact_message = ContactMessage.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message'],
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')
                return redirect('main:contact')
                
            except Exception as e:
                logger.error(f"خطأ في إرسال رسالة التواصل: {e}")
                messages.error(request, 'حدث خطأ أثناء إرسال الرسالة. يرجى المحاولة مرة أخرى.')
    else:
        form = ContactForm()
    
    return render(request, 'main/contact.html', {'form': form})


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe_view(request):
    """الاشتراك في النشرة الإخبارية"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'البريد الإلكتروني مطلوب'})
        
        form = NewsletterForm({'email': email})
        if not form.is_valid():
            return JsonResponse({'success': False, 'message': form.errors['email'][0]})
        
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if not created and not newsletter.is_active:
            newsletter.is_active = True
            newsletter.unsubscribed_at = None
            newsletter.save()
        
        return JsonResponse({
            'success': True,
            'message': 'تم الاشتراك في النشرة الإخبارية بنجاح'
        })
        
    except Exception as e:
        logger.error(f"خطأ في الاشتراك في النشرة الإخبارية: {e}")
        return JsonResponse({'success': False, 'message': 'حدث خطأ في الخادم'})


def about_view(request):
    """صفحة من نحن"""
    try:
        site_settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    return render(request, 'main/about.html', {'site_settings': site_settings})


def privacy_policy_view(request):
    """صفحة سياسة الخصوصية"""
    return render(request, 'main/privacy_policy.html')


def terms_of_service_view(request):
    """صفحة شروط الخدمة"""
    return render(request, 'main/terms_of_service.html')


def search_view(request):
    """صفحة البحث"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query),
            status='published'
        ).order_by('-published_at')
        
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'results_count': len(results) if query else 0,
    }
    
    return render(request, 'main/search.html', context)


def category_posts_view(request, slug):
    """منشورات الفئة"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'main/category_posts.html', context)


def tag_posts_view(request, slug):
    """منشورات العلامة"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(
        tags=tag,
        status='published'
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    
    return render(request, 'main/tag_posts.html', context)


def author_posts_view(request, username):
    """منشورات المؤلف"""
    author = get_object_or_404(User, username=username, is_active=True)
    posts = Post.objects.filter(
        author=author,
        status='published'
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    
    return render(request, 'main/author_posts.html', context)