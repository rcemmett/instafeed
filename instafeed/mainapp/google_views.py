from django.http import HttpResponse, HttpResponseRedirect
import json
import google_api

"""
Main use case flows:
    1) Ask for users' posts
    2) Check session for valid token
    3) If valid, use to get posts and return
    4) If not valid or non existent check database for refresh token
    5) If refresh token, use to get access token, cache access token in session
      get posts, return
    6) If no refresh token, go to signin

    1) Ask to signin user
    2) Check for valid refresh token in database
    3) If valid refresh token then return success (user is signed in)
    4) If no valid refresh token then redirect to google
    5) if callback fails return fail
    6) if callback succeeds, put refresh token into db, get access token, cache
      access token into session.
"""

def google_signin(request):
  response = {}
  if not request.user.is_authenticated():
    response['success'] = False
    response['message'] = "User not authenticated"
    return HttpResponse(json.dumps(response))

  account = GoogleAccount.get_account(request.user)
  if account is None:
    redirect = _request_refresh_token(request)
    redirect['success'] = True
    redirect['message'] = "User redirected to G+ for signin"
    return redirect

  response['refresh_token'] = account.refresh_token
  return HttpResponse(json.dumps(response))

def google_request_token(request, refresh_token):
  account = GoogleAccount.get_account(request.user)
  refresh_token = _request_refresh_token(request) if not account else \
                  account.refresh_token

def google_get_posts(request):
  response = {}
  token = request.session.get('google_token')
  if (token is None) or (not is_valid(token)):
    token = google_request_token(request)

  return HttpResponse(json.dumps(response), 'application/json')


def google_request_code(request):
  url = google_api.request_code()
  return HttpResponseRedirect(url)

def _request_refresh_token(request):
  request_post = google_api.request_token(request.code)
  url = google_api.request_token_url()
  redirect = HttpResponseRedirect(url)
  redirect.POST.update(request_post)

  return redirect

# returns a json object with the following fields:
#   authorized - A boolean representing whether the user gave us access
def google_callback_code(request):
  response = {}
  response['authorized'] = (request.GET.get('error') != 'access_denied')
  if response['authorized']:
    response['code'] = request.GET.get('code')

  return HttpResponse(json.dumps(response))

def google_callback_token(request):
  pass
