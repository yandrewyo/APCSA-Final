from django.shortcuts import render
from django.http import HttpResponse
from main.models import Info
from main.forms import InfoForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import os

# Create your views here.

fetched = True


def index(request):
    context = {}
    context["info"] = Info.objects.all()
    context["form"] = InfoForm()
    context["title"] = "Home"
    return render(request, "index.html", context)


def swimmerPage(request):
    context = {}
    form = InfoForm()
    context["title"] = "Home"

    if request.method == "POST":
        if "search" in request.POST:
            context["name"] = request.POST["name"]
            context["team"] = request.POST["team"]
            swimmer = get_swimmer(request.POST["name"], request.POST["team"])
            results = context["events"] = swimmer[0]
            meets = context["meets"] = swimmer[1]
            pbs = context["pbs"] = swimmer[2]
            best_performances = context["best_performances"] = swimmer[3]
            test = request.POST.copy()
            test.update({"events": results})
            test.update({"meets": meets})
            test.update({"pbs": pbs})
            test.update({"best_performances": best_performances})
            form = InfoForm(test)
            if fetched:
                form.save()
            context["form"] = form
        elif "load" in request.POST:
            for i in Info.objects.all():
                if i.name == request.POST["load"]:
                    form = InfoForm(i)
                    context["name"] = i.name
                    context["team"] = i.team
                    context["events"] = i.events
                    context["meets"] = i.meets
                    context["pbs"] = i.pbs
                    context["best_performances"] = i.best_performances
                    break
    return render(request, "swimmerPage.html", context)


def event(request):
    context = {}
    if request.method == "POST":
        if "events" in request.POST:
            context["form"] = Info.objects.get(name=request.POST["name"])
            context["events"] = context["form"].events
            context["event"] = request.POST["events"]
            context["pbs"] = context["form"].pbs
            context["best_performances"] = context["form"].best_performances
            if context["event"] in context["form"].goals:
                context["goal"] = context["form"].goals[context["event"]]
        # if "setGoal" in request.POST:
        #     updated_form = context["form"].goals.copy()
        #     updated_form[context["event"]] = request.POST["goal"]
        #     context["form"].update({"goals": updated_form})
        #     InfoForm(context["form"]).save()
        #     context["form"] = Info.objects.get(name=request.POST["name"])
        #     print(request.POST)
    return render(request, "event.html", context)


def get_swimmer(name, team):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    import time
    from collections import OrderedDict

    global fetched

    for i in Info.objects.all():
        if i.name == name and i.team == team:
            fetched = False
            return [i.events, i.meets, i.pbs, i.best_performances]

    first_name = name[0 : name.index(" ")]
    last_name = name[name.index(" ") + 1 :]
    team_name = team

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    driver.get("https://www.usaswimming.org/times/individual-times-search")
    wait = WebDriverWait(driver, 10)

    driver.find_element(
        by=By.ID, value="CybotCookiebotDialogBodyLevelButtonAccept"
    ).click()

    driver.find_element(
        by=By.ID, value="Times_TimesSearchDetail_Index_Div-1-FirstName"
    ).send_keys(first_name)
    driver.find_element(
        by=By.ID, value="Times_TimesSearchDetail_Index_Div-1-LastName"
    ).send_keys(last_name)
    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'span[aria-owns="Times_TimesSearchDetail_Index_Div-1-ReportingYearKey_listbox"]',
            )
        )
    ).click()
    time.sleep(0.1)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'All')]"))
    ).click()
    driver.find_element(
        by=By.ID, value="Times_TimesSearchDetail_Index_Div-1-Advanced-Search"
    ).click()
    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'span[aria-owns="Times_TimesSearchDetail_Index_Div-1-SortBy1_listbox"]',
            )
        )
    ).click()
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Swim Date')]"))
    ).click()

    time.sleep(1)
    driver.find_element(
        by=By.ID, value="Times_TimesSearchDetail_Index_Div-1-Search"
    ).click()
    time.sleep(1)

    wait.until(EC.invisibility_of_element((By.CLASS_NAME, "k-loading-mask")))
    results = driver.find_elements(
        By.XPATH, "//*[@id='Times_TimesSearchDetail_Index_Div-1-Times']/table/tbody/tr"
    )
    for i in results:
        data = i.find_elements(By.CSS_SELECTOR, "td:not(.usas-hide-desktop)")
        if (
            driver.execute_script("return arguments[0].textContent;", data[1])
            .strip()
            .lower()
            == team_name
        ):
            driver.execute_script(
                data[3].find_element(By.TAG_NAME, "a").get_attribute("onclick")
            )
            break

    times = {}
    meets = {}
    pbs = {}
    time.sleep(1)
    wait.until(EC.invisibility_of_element((By.CLASS_NAME, "k-loading-mask")))
    time_results = driver.find_elements(
        By.XPATH, "//*[@id='Times_TimesSearchDetail_Index_Div-1-Times']/table/tbody/tr"
    )

    for i in time_results:
        data = i.find_elements(By.CSS_SELECTOR, "td:not(.usas-hide-desktop)")
        event = driver.execute_script("return arguments[0].textContent;", data[0])
        info = {
            "Time": driver.execute_script("return arguments[0].textContent;", data[1]),
            "Age": driver.execute_script("return arguments[0].textContent;", data[3]),
            "Power Points": driver.execute_script(
                "return arguments[0].textContent;", data[4]
            ),
            "Time Standard": driver.execute_script(
                "return arguments[0].textContent;", data[5]
            ),
            "Meet": driver.execute_script("return arguments[0].textContent;", data[6]),
            "Club": driver.execute_script("return arguments[0].textContent;", data[8]),
            "Date": driver.execute_script("return arguments[0].textContent;", data[9]),
        }
        pb_order = ["Time", "Power Points", "Time Standard", "Age", "Date", "Meet"]
        if event not in pbs:
            pbs[event] = {key: info.copy()[key] for key in pb_order if key in pb_order}
            info["Improvement"] = ""
        else:
            improvement = round(
                toSeconds(info["Time"]) - toSeconds(pbs[event]["Time"]), 2
            )
            info["Improvement"] = f"{improvement}"
            if improvement < 0:
                pbs[event] = {
                    key: info.copy()[key] for key in pb_order if key in pb_order
                }
        meet_name = driver.execute_script("return arguments[0].textContent;", data[6])

        if event not in times:
            times[event] = [info.copy()]
        else:
            times[event].append(info.copy())

        del info["Meet"]
        if meet_name not in meets:
            info["Name"] = event
            meets[meet_name] = {
                "Date": driver.execute_script(
                    "return arguments[0].textContent;", data[9]
                ),
                "Age": driver.execute_script(
                    "return arguments[0].textContent;", data[3]
                ),
                "Club": driver.execute_script(
                    "return arguments[0].textContent;", data[8]
                ),
            }
            del info["Date"]
            del info["Age"]
            del info["Club"]
            meets[meet_name]["Events"] = [info]
        else:
            del info["Date"]
            del info["Age"]
            del info["Club"]
            info["Name"] = event
            meets[meet_name]["Events"].append(info)
    print(pbs)
    reversed_meets = {}
    for key, val in reversed(meets.items()):
        reversed_meets[key] = val
    fetched = True
    event_order = [line.strip() for line in open("main/eventlist.txt", "r")]
    event_names = [
        "50 FR",
        "100 FR",
        "200 FR",
        "500 FR",
        "1000 FR",
        "1650 FR",
        "100 BK",
        "200 BK",
        "100 BR",
        "200 BR",
        "100 FL",
        "200 FL",
        "200 IM",
        "400 IM",
    ]
    ordered_pbs = {i: {} for i in event_names}
    for key in event_order:
        if key in pbs:
            for k in ordered_pbs:
                if k in key:
                    ordered_pbs[k][key[len(key) - 3 :]] = pbs[key]

    best_performances = {}
    for i in times:
        if i in event_order:
            max_points = {"Power Points": "0"}
            for j in times[i]:
                if int(j["Power Points"].strip('"')) > int(max_points["Power Points"].strip('"')):
                    max_points = j.copy()
            best_performances[i] = max_points
    print(best_performances)
    for i in best_performances:
        best_performances[i] = {key: best_performances.copy()[i][key] for key in pb_order if key in pb_order}
    ordered_performances = {i: {} for i in event_names}
    for key in event_order:
        if key in best_performances:
            for k in ordered_performances:
                if k in key:
                    ordered_performances[k][key[len(key) - 3 :]] = best_performances[key]

    return [
        {key: list(reversed(times[key])) for key in times},
        reversed_meets,
        ordered_pbs,
        ordered_performances
        #{key: ordered_performances.copy()[key] for key in pb_order if key in pb_order}
    ]


def toSeconds(str):
    arr = str.split(":")
    if len(arr) > 1:
        return float(arr[0]) * 60 + float(arr[1])
    else:
        return float(arr[0])
