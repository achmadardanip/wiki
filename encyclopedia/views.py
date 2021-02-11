from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from markdown2 import Markdown
import secrets
from django import forms
from . import util

markdowner = Markdown()

class createNewEntry(forms.Form):
    title = forms.CharField(label="Entry title", widget=forms.TextInput(attrs={'class': 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8', 'rows': 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })

def get_page(request, title):
    page = util.get_entry(title)

    if page is not None:
        page_converted = markdowner.convert(page)
        return render(request, "encyclopedia/titlepage.html", {
            'title': title,
            'content': page_converted
        })
    else:
        return render(request, "encyclopedia/error.html")

def create(request):
    if request.method == "POST":
        form = createNewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("wiki:title", kwargs={'title': title}))
            else:
                return render(request, "encyclopedia/newEntry.html", {
                    "form": form,
                    "isExist": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/newEntry.html", {
                "form": form,
                "isExist": False
            })
    else:
        return render(request, "encyclopedia/newEntry.html", {
            "form": createNewEntry(),
            "isExist": False
        })

def search(request):
    value = request.GET.get('q','')
    if (util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("wiki:title", kwargs={'title': value}))
    else:
        subStringEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subStringEntries.append(entry)
        
        return render(request, "encyclopedia/search.html", {
            "entries": subStringEntries,
            "search": True,
            "value": value
        })

def edit(request, title):
    entryPage = util.get_entry(title)
    if entryPage is None:
        return render(request, "encyclopedia/error.html")
    else:
        form = createNewEntry()
        form.fields["title"].initial = title
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newEntry.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entryTitle": form.fields["title"].initial
        })

def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse('wiki:title', kwargs={'title': randomEntry}))






