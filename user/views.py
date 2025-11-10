from django.shortcuts import render


def hello_user(request):
    """Simple view that greets a user by name from query parameter."""
    username = request.GET.get('user', 'Guest')
    context = {
        'username': username
    }
    return render(request, 'user/hello.html', context)
