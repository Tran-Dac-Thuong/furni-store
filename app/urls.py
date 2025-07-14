from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from .forms import LoginForm, PasswordResetForm, PasswordChangeForm, PasswordSetForm

class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

urlpatterns = [
    path('', views.home, name='home'),
    path('paypal/create/', views.create_paypal_payment, name='paypal_create'),
    path('paypal/execute/', views.execute_paypal_payment, name='paypal_execute'),
    path('category/<slug:val>', views.category, name='category'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-cart/', views.remove_cart, name='remove_cart'),
    path('order-history/', views.order_history, name='order_history'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop, name='shop'),
    path('detail/<int:id>', views.shop_detail, name='detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('registration/', views.customerregistration, name='customerregistration'),
    path('login/', CustomLoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=PasswordResetForm), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html', form_class=PasswordSetForm), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='app/password_change.html', form_class=PasswordChangeForm, success_url="/"), name='password_change'),
    path('profile/', views.profile, name='profile'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('accounts/', include('allauth.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)