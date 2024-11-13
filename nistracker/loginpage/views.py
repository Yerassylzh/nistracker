from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render

from loginpage.forms import LoginForm
from manage import diary_driver, worker_thread, is_diary_ready
from core.thread_worker import Task


def login(request: HttpRequest):
    form = LoginForm()
    if request.method.upper() == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():  
            pin = form.cleaned_data["pin"]
            password = form.cleaned_data["password"]

            diary_driver.login_result_dict = dict()
            task = Task(diary_driver.login, args=[pin, password], kwargs={}, result_dict=diary_driver.login_result_dict, asynchronous=True)
            worker_thread.add_task(task)

            return JsonResponse({"success": True, "status": "loading"})
        return JsonResponse({"success": False, "errors": form.errors})
    
    if request.method.upper() == "GET":
        if "action" in request.GET and request.GET["action"] == "check status":
            if len(is_diary_ready) == 0 or "result" not in diary_driver.login_result_dict:
                return JsonResponse({"status": "loading"})
            if diary_driver.login_result_dict["result"][0]:
                return JsonResponse({"status": "success"})
            if diary_driver.login_result_dict["result"][0]:
                return JsonResponse({"status": "failure", "message": diary_driver.login_result_dict["result"][1]})

    context = {
        "form": form,
    }

    return render(request, "loginpage/loginpage_light.html", context=context)
