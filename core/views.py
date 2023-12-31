from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.views import generic
from .forms import ContactForm

class HomeView(generic.TemplateView):
    template_name = 'index.html'


class ContactView(generic.FormView):
    form_class = ContactForm
    template_name = 'contact.html'  

    def get_success_url(self):
        return reverse("contact")

    def form_valid(self, form):
        messages.info(self.request, "Thanks for getting in touch. we received your message.")
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message = form.cleaned_data.get('message')

        full_message = f"""
        Received message below from {name}, {email}
        _____________________________


        {message}
        """

        send_mail(
            subject="Received contact from submission",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL]
        )


        return super(ContactView, self).form_valid(form)