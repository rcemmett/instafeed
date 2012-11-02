from django.http import HttpResponse
from django.shortcuts import render, redirect
from emailusernames.forms import EmailUserCreationForm, EmailAuthenticationForm
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
import twitter_api
import facebook_api
import models

def feed(request):
  return render(request, 'Feed.html')

def index(request):
  # Just trying... if cookies are set, then we can just redirect them to feed page
  sid = request.COOKIES.get('sessionid', None)
  uid = request.COOKIES.get('uid', None)
  # TODO also check expiration date/time
  if sid is None or uid is None:
    return signin(request)
  else:
    return feed(request)

def signup(request):
  if request.method == 'POST':
    form = EmailUserCreationForm(request.POST)
    if form.is_valid():
      message = None

      email = form.clean_email()
      password = form.clean_password2()
      form.save()

      user = authenticate(email=email, password=password)
      if (user is not None) and (user.is_active):
        login(request, user)
        message = "Registration successful"
      else:
        message = "There was an error automatically logging you in. Try <a href=\"/index/\">logging in</a> manually."

      # TODO: fixed the rendering once homepage is ready
      return redirect('/feed/', {'username': email, 'message': message})

  else:
    form = EmailUserCreationForm()

  return render(request, 'signup.html', {'form': form})

def signin(request):
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(email=email, password=password)
    if (user is not None) and (user.is_active):
      login(request, user)
      return redirect('/feed/', {'username': email})
    else:
      return render(request, 'index.html', {'username': email})
  else:
    form = EmailAuthenticationForm()

  return render(request, 'index.html', {'form': form})

#Tag needed for ajax call. May need to take this out later to protect from attacks(?)
@csrf_exempt
def twitter_request(request):
  try:
    #grabs tokens from the db
    one_user = TwitterAccount.objects.get(user_id=request.user.id)
  except Entry.DoesNotExist:
    return HttpResponse("failed to get data for user")
  json = request.POST
  if json.get('type') == 'upload':
    print "trying to post"
    twitter_api.twitter_post(one_user.access_token, one_user.access_secret, json.get('message'))
  elif json.get('type') == 'feedRequest':
    #get stuff from twitter
    print "requesting posts from twitter"
    twitter_post = twitter_api.twitter_user_timeline(one_user.access_token, one_user.access_secret, 10)
  return HttpResponse(json)

@csrf_exempt
def facebook_request(request):
  json = request.POST
  if json.get('type') == 'upload':
    #post to fb
    pass
  elif json.get('type') == 'feedRequest':
    #get stuff from fb
    pass
  return HttpResponse("Hello")
  return HttpResponse(json)

def accounts(request):
  return render(request, 'Accounts.html')

@csrf_exempt
def facebook_signin(request):
  #TODO: flesh out facebook sign in, add tokens to database
  f = facebook_api.facebook_auth()
  response['success'] = 'true';
  return HttpResponse(json.dumps(reponse))

@csrf_exempt
def twitter_signin(request):
  t = twitter_api.twitter_authentication_url()
  request.session['request_token'] = t[1]
  request.session['request_secret'] = t[2]
  return HttpResponse(t[0])

#need to test this
def twitter_callback(request):
  verifier = request.GET.get('oauth_verifier')
  token_info = twitter_api.twitter_authenticate(verifier, request.session['request_token'], request.session['request_secret'])
  user = request.user
  twitter_account = TwitterAccount(user_id=user.id, access_token=token_info[0], access_secret=token_info[1])
  twitter_account.save()
  return render(request, 'Accounts.html')
