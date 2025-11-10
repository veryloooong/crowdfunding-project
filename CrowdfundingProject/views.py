from django.shortcuts import render


def home(request):
    """Simple home view that renders the Hello World template."""
    return render(request, 'home.html')
