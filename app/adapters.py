from allauth.account.adapter import DefaultAccountAdapter

class NoMessageAccountAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        if 'account/messages/logged_in.txt' in message_template:
            return  # Không hiện message đăng nhập thành công
        super().add_message(request, level, message_template, message_context, extra_tags)