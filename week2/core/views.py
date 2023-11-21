from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CatalogRequestForm, CategoryForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CatalogRequest, Category, Profile
from django import forms


@login_required
def catalog(request):
    return render(request, 'index.html')


@login_required
def profil(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            u = user_form.save()
            user_form.save()
            profile_form.save()
            messages.success(request, f'Ваш аккаунт был обновлен!')
            return redirect('profil')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'user/profil.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            u = form.save()
            profile = Profile.objects.create(user=u)    
            messages.success(
                request, f'You have been registered , you can login now')
            profile.save()
            u.save()
            return redirect('index')
    else:
        form = UserRegisterForm()
        print(form.errors)

    return render(request, 'user/register.html', {'form': form})


@login_required
def catalog_request_create(request):
    if request.method == 'POST':
        form = CatalogRequestForm(request.POST, request.FILES)
        if form.is_valid():
            catalog_request = form.save(commit=False)
            catalog_request.user = request.user
            catalog_request.status = 'new'
            catalog_request.save()
            return redirect('catalog_request_detail', pk=catalog_request.pk)
    else:
        form = CatalogRequestForm()
        form.fields['status'].widget.attrs['disabled'] = True
        if not request.user.is_superuser:
            form.fields['status'].widget = forms.HiddenInput()
            form.fields['image_after'].widget = forms.HiddenInput()
            form.fields['comment'].widget = forms.HiddenInput()
    return render(request, 'catalog/catalog_request_form.html', {'form': form, "action": "create"})


@login_required
def catalog_request_edit(request, pk):
    catalog_request = get_object_or_404(CatalogRequest, pk=pk)
    if request.method == 'POST':
        form = CatalogRequestForm(
            request.POST, request.FILES, instance=catalog_request)
        if form.is_valid():
            catalog_request = form.save(commit=False)
            if catalog_request.status == 'in_progress' and not catalog_request.comment:
                form.add_error(
                    'comment', 'При изменении статуса на "Принято в работу" необходимо указать комментарий.')
            elif catalog_request.status == 'completed' and not catalog_request.image_after:
                form.add_error(
                    'image_after', 'При изменении статуса на "Выполнено" необходимо прикрепить изображение.')
            else:
                catalog_request.save()
                return redirect('catalog_request_detail', pk=catalog_request.pk)
    else:
        if not request.user.is_superuser:
            form = CatalogRequestForm(instance=catalog_request, initial={
                                      'status': catalog_request.status})
            form.fields['status'].widget = forms.HiddenInput()
            form.fields['image_after'].widget = forms.HiddenInput()
            form.fields['comment'].widget = forms.HiddenInput()
        else:
            form = CatalogRequestForm(instance=catalog_request)
            if catalog_request.status == 'new':
                form.fields['status'].choices = [
                    ("in_progress", "Принято в работу"), ("completed", "Выполнено")]
            elif catalog_request.status == 'in_progress':
                form.fields['status'].choices = [("completed", "Выполнено"),]

    return render(request, 'catalog/catalog_request_form.html', {'form': form, "action": "edit"})


@login_required
def catalog_request_delete(request, pk):
    if request.user.is_superuser:
        catalog_request = get_object_or_404(CatalogRequest, pk=pk)
    else:
        catalog_request = get_object_or_404(
            CatalogRequest, pk=pk, user=request.user)

    catalog_request.delete()
    return redirect('catalog_request_list', username=request.user.username)


@login_required
def catalog_request_list(request, username=None):
    status = request.GET.get("status")
    user = get_object_or_404(User, username=request.user.username)

    if user.is_superuser:
        catalog_requests = CatalogRequest.objects.all()
        context = {'catalog_requests': catalog_requests}

        if status:
            catalog_requests = CatalogRequest.objects.filter(
                status=status).order_by("created_at")
            context = {'catalog_requests': catalog_requests, "status": status}

        if username:
            user = get_object_or_404(User, username=username)
            catalog_requests = CatalogRequest.objects.filter(user=user)
            context = {'catalog_requests': catalog_requests, "status": status}

        return render(request, 'catalog/user_catalog_requests.html', context)

    else:
        catalog_requests = CatalogRequest.objects.filter(user=user)
        len_catalog_request = CatalogRequest.objects.filter(user=user).count()
        context = {'catalog_requests': catalog_requests}

        if request.GET.get("sort") and request.GET.get("filter"):
            query = request.GET.get("filter")
            catalog_requests = CatalogRequest.objects.filter(
                user=user, status="completed").order_by("created_at")[:4]
            catalog_request_count = CatalogRequest.objects.filter(
                user=user, status="in_progress").count()
            len_catalog_request = CatalogRequest.objects.filter(
                user=user, status="completed").count()

            context = {'catalog_requests': catalog_requests, "query": query, "catalog_request_count":
                       catalog_request_count, "page": "home", "len_catalog_request": len_catalog_request}

        if status:
            catalog_requests = catalog_requests = CatalogRequest.objects.filter(
                user=user, status=status).order_by("created_at")
            context = {'catalog-requests': catalog_requests, "status": status}

        return render(request, 'catalog/user_catalog_requests.html', context)


@login_required
def catalog_request_detail(request, pk):
    catalog_request = get_object_or_404(CatalogRequest, pk=pk)
    return render(request, 'catalog/catalog_request_detail.html', {'catalog_request': catalog_request})


@login_required
@user_passes_test(lambda user: user.is_superuser)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('category-detail', pk=category.pk)
    else:
        form = CategoryForm()
    return render(request, 'category/category-form.html', {'form': form, "action": "create"})


@login_required
@user_passes_test(lambda user: user.is_superuser)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            return redirect('category-detail', pk=category.pk)
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category/category-form.html', {'form': form, "action": "edit"})


@login_required
@user_passes_test(lambda user: user.is_superuser)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category-list')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category/category-list.html', {'categories': categories})


@login_required
@user_passes_test(lambda user: user.is_superuser)
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'category/category-detail.html', {'category': category})

