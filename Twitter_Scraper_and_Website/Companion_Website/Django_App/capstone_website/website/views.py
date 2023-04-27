from django.shortcuts import render


def index(request): #creating the url connection for the home page
    return render(request, 'index.html', {})
def about(request):#creating the url connection for the help page
    return render(request, 'about.html', {})
