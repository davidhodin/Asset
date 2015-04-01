#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.shortcuts import render
from django.core.urlresolvers import reverse
from SAM.models import ConnexionForm

# Vue vers la page d'accueil
def start(request):
	return render_to_response('Start.html')

def connexion(request):
    error = False
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]  # Nous récupérons le nom d'utilisateur
            password = form.cleaned_data["password"]  # … et le mot de passe
            user = authenticate(username=username, password=password)  #Nous vérifions si les données sont correctes
            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'utilisateur
                return redirect('/')
            else: #sinon une erreur sera affichée
                error = True
    else:
        form = ConnexionForm()
    return render(request, 'connexion.html',locals())

def deconnexion(request):                                                                               
    logout(request)
    return redirect('/connexion/')