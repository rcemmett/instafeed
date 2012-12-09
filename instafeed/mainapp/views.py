from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from emailusernames.forms import EmailUserCreationForm, EmailAuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from models import ScheduledUpdates, TwitterAccount, FacebookAccount, Account
import datetime, traceback, json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz


@login_required
def feed(request):
  return render(request, 'Feed.html')

@login_required
def index(request):
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

      # Since user does not have any accounts by the time they signe in,
      # we should redirect them to accounts page instead of feed page.
      return redirect('/feed/')

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
      facebook_account = FacebookAccount.get_account(request_id=request.user.id)
      twitter_account = TwitterAccount.get_account(request_id=request.user.id)
      if facebook_account is None and twitter_account is None:
        return redirect('/feed/', {'username': email})
      else:
        return redirect('/feed/', {'username': email})
    else:
      form = EmailAuthenticationForm()
      form.non_field_errors = 'Your email and password were incorrect.'
      return render(request, 'index.html', {'form': form})
  else:
    form = EmailAuthenticationForm()

  return render(request, 'index.html', {'form': form})

def faq_request(request):
  return render(request, 'faq.html')

@login_required
def settings(request):
  return render(request, 'settings.html')

@login_required
def logoutuser(request):
  logout(request)
  return redirect('/')

@login_required
def accounts(request):
  return render(request, 'Accounts.html')

def schedule(request):
  now = datetime.datetime.now()
  year_list = [now.year, now.year + 1]
  month_list = [x for x in range(1, 13)]
  day_list = [x for x in range(1, 32)]
  hour_list = [x for x in range(0, 24)]
  minute_list = [x for x in range(0, 60)]
  posts = ScheduledUpdates.objects.filter(user_id = request.user).order_by(
      "publish_date") if request.user else []
  return render(request, 'schedule.html', {'year_list': year_list, \
      'month_list': month_list, 'day_list': day_list, \
      'hour_list': hour_list, 'minute_list': minute_list, 'posts': posts})

@csrf_exempt
def delete_scheduled_update(request):
  post_id = request.POST.get('post_id')
  post = ScheduledUpdates.objects.get(id = post_id)
  post.delete()
  return_dict = {'success': 'false'}
  return HttpResponse(json.dumps(return_dict), mimetype="application/json")

@csrf_exempt
def scheduled_update(request):
  request_json = request.POST
  year = int(request_json.get('year'))
  month = int(request_json.get('month'))
  day = int(request_json.get('day'))
  hour = int(request_json.get('hour'))
  minute = int(request_json.get('minute'))
  second = int(request_json.get('second'))
  microsecond = int(request_json.get('microsecond'))
  tz = request_json.get('timezone')
  date_to_post = datetime.datetime(year, month, day, hour, minute, second,
                                   microsecond)
  try:
    date_to_post = timezone.make_aware(date_to_post, pytz.timezone(tz))
  except:
    date_to_post = timezone.make_aware(date_to_post, timezone.utc)
  now = datetime.datetime.now()
  try:
    now = timezone.make_aware(now, pytz.timezone(tz))
  except:
    now = timezone.make_aware(now, pytz.timezone(timezone.utc))
  if now > date_to_post:
    return_dict = {'success': 'false'}
    return_dict['error'] = 'invalid date'
    return_json = json.dumps(return_dict)
    return HttpResponse(return_json, status=400, mimetype="application/json")
  site = int(request_json.get('post_site'))
  scheduled_update_entry = ScheduledUpdates.objects.create(
                                            user_id=request.user,
                                            update=request_json.get('message'),
                                            publish_date=date_to_post,
                                            publish_site=site)
  preceding_id = scheduled_update_entry.get_previous_id()
  return_dict = {'success': 'true'}
  return_dict['rendered_update'] = render_to_string('schedule_post.html',
      {'post': scheduled_update_entry})
  return_dict['preceding_id'] = preceding_id
  return HttpResponse(json.dumps(return_dict), mimetype="application/json")

