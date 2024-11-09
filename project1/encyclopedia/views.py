from django.shortcuts import render,redirect

from . import util
import random, markdown2


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry_page(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page {title} does not exist."
        })
    
    html_content = util.markdown_to_html(content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get("q", "").strip()
    all_entries = util.list_entries()
    
    exact_match = next((entry for entry in all_entries if entry.lower() == query.lower()), None)
    if exact_match:
        return redirect("entry_page", title=exact_match)
    
    results = [entry for entry in all_entries if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search_results.html", {
        "query": query,
        "results": results
    })

def newpage(request):
    if request.method == "POST":
        title = request.POST.get("title").strip()
        content = request.POST.get("content").strip()

        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/error.html", {
                "message": "An encyclopedia entry already exists with that title."
            })
        
        # Save the new entry
        util.save_entry(title, content)
        return redirect("entry_page", title=title)

    return render(request, "encyclopedia/newpage.html")

def edit(request, title):
    entry_content = util.get_entry(title)

    if entry_content is None: # the entry doesn't exist
        return render(request, "encyclopedia/error.html", {
            "message": f"The entry { title } doesn't exist."
        })
    
    if request.method == "POST":
        new_content = request.POST.get("content").strip()
        util.save_entry(title, new_content)
        return redirect("entry_page", title=title)

    return render(request, "encyclopedia/editpage.html", {
        "title": title,
        "content": entry_content
    })

def randompage(request):
    entries = util.list_entries() 
    random_entry = random.choice(entries)  # To choose a random page from the list
    return redirect("entry_page", title=random_entry)