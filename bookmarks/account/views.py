from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .forms import (
    LoginForm, UserRegistrationForm, UserEditForm, 
    ProfileEditForm, PostForm, CommentForm
)
from .models import Profile, Post, Comment, Like, Follow


# --- ویوهای ثبت‌نام و احراز هویت (همان قبلی) ---

def landing(request):
    """Landing page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'account/landing.html')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)  # ساخت پروفایل خودکار
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard')


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, 
            data=request.POST, 
            files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {
        'user_form': user_form, 
        'profile_form': profile_form
    })


# --- ویوهای جدید: داشبورد و پست‌ها ---

@login_required
def dashboard(request):
    """نمایش پست‌های کاربرانی که فالو کرده + پست‌های خود کاربر"""
    # گرفتن کاربرانی که فالو کرده
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    # پست‌ها: پست‌های فالو شده‌ها + پست‌های خود کاربر
    posts = Post.objects.filter(
        Q(author_id__in=following_ids) | Q(author=request.user)
    ).select_related('author', 'author__profile').prefetch_related('likes', 'comments').order_by('-created')
    
    post_form = PostForm()
    
    return render(request, 'account/dashboard.html', {
        'section': 'dashboard',
        'posts': posts,
        'post_form': post_form,
    })


@login_required
def post_create(request):
    """ساخت پست جدید"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('dashboard')
    else:
        form = PostForm()
    return render(request, 'account/post_create.html', {'form': form})


@login_required
def post_like(request, post_id):
    """لایک یا آنلایک کردن یک پست"""
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        # اگر قبلاً لایک کرده بود، آنلایک کن
        like.delete()
    
    # برگرد به صفحه‌ای که از آنجا آمده
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def post_detail(request, post_id):
    """نمایش جزئیات یک پست با کامنت‌ها"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile').prefetch_related('comments', 'comments__user', 'likes'),
        id=post_id
    )
    comments = post.comments.select_related('user').all()
    comment_form = CommentForm()
    is_liked = Like.objects.filter(post=post, user=request.user).exists()
    
    return render(request, 'account/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
    })


@login_required
def add_comment(request, post_id):
    """اضافه کردن کامنت به یک پست"""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Comment added!')
    return redirect('post_detail', post_id=post.id)


# --- ویوهای جدید: فالو و کاربران ---

@login_required
def user_follow(request, user_id):
    """فالو یا آنفالو کردن یک کاربر"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.warning(request, "You cannot follow yourself!")
        return redirect('user_list')
    
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user)
    
    if not created:
        # اگر قبلاً فالو کرده بود، آنفالو کن
        follow.delete()
        messages.success(request, f'Unfollowed {user.username}')
    else:
        messages.success(request, f'Following {user.username}')
    
    return redirect(request.META.get('HTTP_REFERER', 'user_list'))


@login_required
def user_list(request):
    """لیست کاربران برای فالو کردن"""
    query = request.GET.get('q', '')
    users = User.objects.select_related('profile').filter(is_active=True).exclude(id=request.user.id)
    
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    # اضافه کردن وضعیت فالو برای هر کاربر
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    return render(request, 'account/user_list.html', {
        'section': 'peoples',
        'users': users,
        'following_ids': following_ids,
        'query': query,
    })


@login_required
def user_profile(request, username):
    """نمایش پروفایل یک کاربر"""
    user = get_object_or_404(
        User.objects.select_related('profile'),
        username=username
    )
    posts = Post.objects.filter(author=user).order_by('-created')
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    return render(request, 'account/user_profile.html', {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
    })


# --- ویوهای قدیمی (می‌تونی حذف کنی یا نگه داری) ---

