import json

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render(request, 'home/index.html')


@csrf_exempt
def power_api(request):
    if request.method == 'GET':
        return JsonResponse({'state': cache.get('power_state', 'off')})

    if request.method != 'POST':
        return JsonResponse({'error': 'Use GET or POST.'}, status=405)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Request body must be valid JSON.'}, status=400)

    state = payload.get('state')
    if state not in {'on', 'off'}:
        return JsonResponse({'error': 'state must be "on" or "off".'}, status=400)

    cache.set('power_state', state, timeout=None)
    return JsonResponse({'state': state})


def resister(request):
    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')

        if User.objects.filter(email__iexact=email).exists():
            error = 'An account with this email already exists.'
        elif password != password_confirmation:
            error = 'Passwords do not match.'
        else:
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            return redirect('login')

    return render(request, 'resister.html', {'error': error})


def login_view(request):
    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        account = User.objects.filter(email__iexact=email).first()
        user = authenticate(
            request,
            username=account.username if account else email,
            password=password,
        )

        if user is not None:
            auth_login(request, user)
            return redirect('home')

        error = 'Invalid email or password.'

    return render(request, 'login.html', {'error': error})
