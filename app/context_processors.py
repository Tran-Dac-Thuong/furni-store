from allauth.socialaccount.models import SocialAccount

def google_avatar(request):
    avatar_url = None
    if request.user.is_authenticated:
        try:
            social_account = SocialAccount.objects.get(user=request.user, provider='google')
            avatar_url = social_account.extra_data.get('picture')
        except (SocialAccount.DoesNotExist, KeyError):
            avatar_url = None
    return {'google_avatar_url': avatar_url} 