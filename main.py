import datetime
import os
import re

from bson import ObjectId
from flask import Flask, request, render_template, session, redirect
import pymongo
my_collections = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_collections['Freelancer']
admin_col = my_db['Admin']
client_col = my_db['Client']
developer_col = my_db['Developer']
category_col = my_db['Category']
project_col = my_db['Project']
application_col = my_db['Application']
reviews_col = my_db['Reviews']
report_col = my_db['Report']
subscription_col = my_db['Subscription']
subscription_plan_col = my_db['Subscription_plan']
chat_col = my_db['Chat']

app = Flask(__name__)
app.secret_key = "freelancer"

App_Root = os.path.dirname(__file__)
App_Root = App_Root + "/static"

status_application_posted = "Client Posted Application"
status_applied_for_project = "Developer Applied for Project"
status_application_accepted = "Application Accepted by Client"
status_application_rejected = "Application rejected by Client"
status_add_schedule = "Schedule Added by Client"
status_schedule_accepted = "Schedule Accepted by Developer"
status_schedule_rejected = "Schedule Rejected by Developer"
status_first_payment = "10% amount Deposited to Developer"
status_Development_Started = "Project Development Started"
status_project_completed = "Project Completed"

if admin_col.count_documents({}) == 0:
    admin_col.insert_one({"name": "admin", "password": "admin", "role": "admin"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")


@app.route("/adminLogin1", methods=['post'])
def adminLogin1():
    name = request.form.get("username")
    password = request.form.get("password")
    query = {"username": name, "password": password}
    admin = admin_col.find_one(query)

    if admin != None:
        session['admin_id'] = str(admin['_id'])
        session['role'] = 'Admin'
        return redirect("/adminHome")
    else:
        return render_template("msg.html", message="Invalid Login Details",  color="text-danger")


@app.route("/adminHome")
def adminHome():
    return render_template("adminHome.html")


@app.route("/clientLogin")
def clientLogin():
    return render_template("clientLogin.html")


@app.route("/clientLogin1", methods=['post'])
def clientLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = client_col.count_documents(query)
    if count > 0:
        client = client_col.find_one(query)
        if client["status"] == "Verified":
            session['client_id'] = str(client['_id'])
            session['role'] = 'Client'
            return redirect("/clientHome")
        else:
            return render_template("msg.html", message="Client is Not Activated",  color="text-danger")
    else:
        return render_template("msg.html", message="Invalid Login Details",  color="text-danger")


@app.route("/clientHome")
def clientHome():
    client_id = session['client_id']
    query = {"_id": ObjectId(client_id)}
    clients = client_col.find(query)
    return render_template("clientHome.html", clients=clients)


@app.route("/clientRegistration")
def clientRegistration():
    return render_template("clientRegistration.html")


@app.route("/clientRegistration1", methods=['post'])
def clientRegistration1():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    address = request.form.get('address')
    about = request.form.get('about')
    status = "Not Verified"
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = client_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details",  color="text-danger")
    else:
        query = {"name": name, "phone": phone, "email": email, "password": password, "address": address, "about": about, "status": status}
    client_col.insert_one(query)
    return redirect("/clientLogin")


@app.route("/viewClients")
def viewClients():
    clients = client_col.find()
    return render_template("viewClients.html", clients=clients)


@app.route("/verifyClient")
def verifyClient():
    client_id = ObjectId(request.args.get("client_id"))
    query = {'_id': ObjectId(client_id)}
    query1 = {"$set": {"status": "Verified"}}
    client_col .update_one(query, query1)
    return redirect("/viewClients")


@app.route("/notVerifyClient")
def notVerifyClient():
    client_id = ObjectId(request.args.get("client_id"))
    query = {'_id': ObjectId(client_id)}
    query1 = {"$set": {"status": "Not Verified"}}
    client_col .update_one(query, query1)
    return redirect("/viewClients")


@app.route("/developerLogin")
def developerLogin():
    return render_template("developerLogin.html")


@app.route("/developerLogin1", methods=['post'])
def developerLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = developer_col.count_documents(query)
    if count > 0:
        developer = developer_col.find_one(query)
        if developer["status"] == "Verified":
            session['developer_id'] = str(developer['_id'])
            session['role'] = 'Developer'
            return redirect("/developerHome")
        else:
            return render_template("msg.html", message="Developer is Not Activated",  color="text-danger")
    else:
        return render_template("msg.html", message="Invalid Login Details",  color="text-danger")


@app.route("/developerHome")
def developerHome():
    developer_id = session['developer_id']
    query = {"_id": ObjectId(developer_id)}
    developers = developer_col.find(query)
    return render_template("developerHome.html", developers=developers)


@app.route("/developerRegistration")
def developerRegistration():
    return render_template("developerRegistration.html")


@app.route("/developerRegistration1", methods=['post'])
def developerRegistration1():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    status = "Not Verified"
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = developer_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details", color="text-danger")
    else:
        query = {"name": name, "phone": phone, "email": email, "password": password, "status": status}
    developer_col.insert_one(query)
    return redirect("/developerLogin")


@app.route("/viewDevelopers")
def viewDevelopers():
    developers = developer_col.find()
    return render_template("viewDevelopers.html", developers=developers)


@app.route("/verifyDeveloper")
def verifyDeveloper():
    developer_id = ObjectId(request.args.get("developer_id"))
    query = {'_id': ObjectId(developer_id)}
    query1 = {"$set": {"status": "Verified"}}
    developer_col .update_one(query, query1)
    return redirect("/viewDevelopers")


@app.route("/notVerifyDeveloper")
def notVerifyDeveloper():
    developer_id = ObjectId(request.args.get("developer_id"))
    query = {'_id': ObjectId(developer_id)}
    query1 = {"$set": {"status": "Not Verified"}}
    developer_col .update_one(query, query1)
    return redirect("/viewDevelopers")


@app.route("/uploadResume")
def uploadResume():
    return render_template("uploadResume.html")


@app.route("/uploadResume1", methods=['post'])
def uploadResume1():
    developer_id = session['developer_id']
    upload_resume = request.files.get("upload_resume")
    path = App_Root + "/resume/" + upload_resume.filename
    upload_resume.save(path)
    query = {'_id': ObjectId(developer_id)}
    query1 = {"$set": {"upload_resume": upload_resume.filename}}
    developer_col.update_one(query, query1)
    return redirect("/developerHome")


@app.route("/categories")
def categories():
    categories = category_col.find()
    return render_template("categories.html", categories=categories)


@app.route("/categories1", methods=['post'])
def categories1():
    category_name = request.form.get("category_name")
    query = {"category_name": category_name}
    category_col.insert_one(query)
    return redirect("/categories")


@app.route("/view_projects")
def view_projects():
    query = {}
    if session['role'] == "Client":
        query = {"client_id": ObjectId(session['client_id'])}
    elif session['role'] == "Admin" or session['role'] == "Developer":
        projects = project_col.find()
        projects_ids = []
        for project in projects:
            projects_ids.append({"_id": project['_id']})
            query = {"$or": projects_ids}

    categories = category_col.find()
    skills = []
    projects = project_col.find()
    for project in projects:
        skills.append(project['skills'])
    skills = set(skills)
    category_id = request.args.get("category_id")
    skill = request.args.get("skill")
    project_title = request.args.get("project_title")

    if category_id == None :
        category_id = ''
    if skill == None:
        skill = ''
    if project_title == None:
        project_title = ''

    if (category_id == '' and skill == '' and project_title == ''):
        if session['role'] == "Client":
            query = {"client_id": ObjectId(session['client_id'])}
        else:
            query = {}
    elif category_id == '' and skill == '' and project_title != '':
        if session['role'] == "Client":
            rgx = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"project_title": rgx, "client_id": ObjectId(session['client_id'])}
        else:
            rgx = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"project_title": rgx}

    elif category_id == '' and skill != '' and project_title == '':
        if session['role'] == "Client":
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            query = {"skills": rgx, "client_id": ObjectId(session['client_id'])}
        else:
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            query = {"skills": rgx}
    elif category_id == '' and skill != '' and project_title != '':
        if session['role'] == "Client":
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            rgx1 = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"skills": rgx, "project_title": rgx1, "client_id": ObjectId(session['client_id'])}
        else:
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            rgx1 = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"skills": rgx, "project_title": rgx1}
    elif category_id != '' and skill == '' and project_title == '':
        if session['role'] == "Client":
            query = {"category_id": ObjectId(category_id), "client_id": ObjectId(session['client_id'])}
        else:
            query = {"category_id": ObjectId(category_id)}

    elif category_id != '' and skill == '' and project_title != '':
        if session['role'] == "Client":
            rgx = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"category_id": ObjectId(category_id), "project_title": rgx,
                     "client_id": ObjectId(session['client_id'])}
        else:
            rgx = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"category_id": ObjectId(category_id), "project_title": rgx}
    elif category_id != '' and skill != '' and project_title == '':
        if session['role'] == "Client":
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            query = {"category_id": ObjectId(category_id), "skill": rgx, "client_id": ObjectId(session['client_id'])}
        else:
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            query = {"category_id": ObjectId(category_id), "skill": rgx}

    elif category_id != '' and skill != '' and project_title != '':
        if session['role'] == "Client":
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            rgx1 = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"category_id": ObjectId(category_id), "skill": rgx, "project_title": rgx1,"client_id": ObjectId(session['client_id'])}
        else:
            rgx = re.compile(".*" + skill + ".*", re.IGNORECASE)
            rgx1 = re.compile(".*" + project_title + ".*", re.IGNORECASE)
            query = {"category_id": ObjectId(category_id), "skill": rgx, "project_title": rgx1}
    project_details = project_col.find(query)
    return render_template("view_projects.html", get_application_by_developer=get_application_by_developer, is_requested_for_application=is_requested_for_application, status_project_completed=status_project_completed, get_project_id_by_application=get_project_id_by_application, get_client_id_by_reviews=get_client_id_by_reviews, categories=categories, skills=skills, project_details=project_details, get_category_id=get_category_id, get_client_id=get_client_id, status_applied_for_project=status_applied_for_project, status_application_posted=status_application_posted, status_add_schedule=status_add_schedule, status_schedule_accepted=status_schedule_accepted, status_Development_Started=status_Development_Started)


@app.route("/add_project")
def add_project():
    categories = category_col.find()
    return render_template("add_project.html", categories=categories)


@app.route("/add_project1", methods=['post'])
def add_project1():
    client_id = session['client_id']
    category_id = request.form.get("category_id")
    project_title = request.form.get("project_title")
    project_cost = request.form.get("project_cost")
    skills = request.form.get("skills")
    description = request.form.get("description")
    date = datetime.datetime.now()
    status = status_application_posted

    project_doc = request.files.get("project_doc")
    path = App_Root +"/document/" + project_doc.filename
    project_doc.save(path)

    query = {"client_id": ObjectId(client_id), "category_id": ObjectId(category_id), "project_title": project_title, "project_cost": project_cost, "skills": skills, "project_doc": project_doc.filename, "description": description, "date": date, "status": status}
    project_col.insert_one(query)
    return redirect("/view_projects")


def get_project_id_by_application(project_id):
    query = {"project_id": ObjectId(project_id), "$or": [{"status": status_application_accepted}, {"status": status_project_completed}]}
    application = application_col.find_one(query)
    if application!=None:
        developer_id = application['developer_id']
        query = {"_id": ObjectId(developer_id)}
        developer = developer_col.find_one(query)
    return None


def get_application_by_developer(project_id):
    query = {"project_id": ObjectId(project_id)}
    application = application_col.find_one(query)
    if application != None:
        developer_id = application['developer_id']
        query = {"_id": ObjectId(developer_id)}
        developer = developer_col.find_one(query)
        return developer


def get_category_id(category_id):
    query = {"_id": ObjectId(category_id)}
    category = category_col.find_one(query)
    return category


def get_client_id(client_id):
    query = {"_id": ObjectId(client_id)}
    client = client_col.find_one(query)
    return client


def get_developer_id(developer_id):
    query = {"_id": ObjectId(developer_id)}
    developer = developer_col.find_one(query)
    return developer


def get_project_id(project_id):
    query = {"_id": ObjectId(project_id)}
    project = project_col.find_one(query)
    return project


@app.route("/apply_for_project")
def apply_for_project():
    project_id = request.args.get("project_id")
    return render_template("apply_for_project.html", project_id=project_id)


@app.route("/apply_for_project1", methods=['post'])
def apply_for_project1():
    developer_id = session['developer_id']
    project_id = request.form.get("project_id")
    upload_resume = request.files.get("upload_resume")
    path = App_Root + "/resume/" + upload_resume.filename
    upload_resume.save(path)
    date = datetime.datetime.now()
    status = status_applied_for_project

    query = {"developer_id": ObjectId(developer_id), "project_id": ObjectId(project_id), "resume": [upload_resume.filename], "date": date, "status": status}
    application_col.insert_one(query)

    return redirect("/view_projects")


@app.route("/view_applied_projects")
def view_applied_projects():
    query = {}
    if session['role'] == "Admin" or session['role'] == "Client":
        project_id = request.args.get("project_id")
        query = {"project_id": ObjectId(project_id)}
    elif session['role'] == "Developer":
        developer_id = session['developer_id']
        query = {"developer_id": ObjectId(developer_id)}
    applications = application_col.find(query)
    return render_template("view_applied_projects.html", applications=applications, get_developer_id=get_developer_id, get_project_id=get_project_id, status_applied_for_project=status_applied_for_project, status_application_accepted=status_application_accepted, get_developer_id_by_reviews=get_developer_id_by_reviews)


@app.route("/accept_application")
def accept_application():
    project_id = request.args.get("project_id")
    application_id = request.args.get("application_id")
    query = {'_id': ObjectId(application_id)}
    query1 = {"$set": {"status": status_application_accepted}}
    application_col .update_one(query, query1)
    query = {"_id": ObjectId(project_id)}
    query2 = {"$set": {"status": "Project Assigned To Developer"}}
    project_col.update_one(query, query2)
    query = {"project_id": ObjectId(project_id), "status": status_applied_for_project}
    query2 = {"$set": {"status": status_application_rejected}}
    application_col.update_many(query, query2)
    return redirect("/view_applied_projects?project_id="+str(project_id))


@app.route("/reject_application")
def reject_application():
    project_id = request.args.get("project_id")
    application_id = request.args.get("application_id")
    query = {'_id': ObjectId(application_id)}
    query1 = {"$set": {"status": status_application_rejected}}
    application_col .update_one(query, query1)
    return redirect("/view_applied_projects?project_id="+str(project_id))


@app.route("/add_schedule")
def add_schedule():
    application_id = request.args.get("application_id")
    return render_template("add_schedule.html", application_id=application_id)


@app.route("/add_schedule1", methods=['post'])
def add_schedule1():
    application_id = request.form.get("application_id")
    query = {"_id": ObjectId(application_id)}
    application = application_col.find_one(query)
    project_id = application['project_id']

    date_time = request.form.get("date_time")
    date_time = date_time.replace("T", " ")
    date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    schedule_status = status_add_schedule
    query = {'$push': {"schedule": {'application_id': ObjectId(application_id),"date_time": date_time, "status": schedule_status}}}
    project_col.update_one({"_id": ObjectId(project_id)}, query)

    query = {'_id': ObjectId(project_id)}
    query1 = {"$set": {"status": status_add_schedule}}
    project_col.update_one(query, query1)
    return redirect("/view_projects")


@app.route("/view_schedule")
def view_schedule():
    project_id = request.args.get("project_id")
    query = {"_id": ObjectId(project_id)}
    projects = project_col.find(query)
    return render_template("view_schedule.html", projects=projects, get_client_id=get_client_id, status_add_schedule=status_add_schedule, get_developer_id_by_application=get_developer_id_by_application, status_schedule_accepted=status_schedule_accepted)


def get_developer_id_by_application(application_id):
    query = {"_id": ObjectId(application_id)}
    application = application_col.find_one(query)
    developer_id = application['developer_id']
    query = {"_id": ObjectId(developer_id)}
    developer = developer_col.find_one(query)
    return developer


@app.route("/viewClientDetails")
def viewClientDetails():
    client_id = request.args.get("client_id")
    query = {"_id": ObjectId(client_id)}
    client = client_col.find_one(query)
    return render_template("viewClientDetails.html", client=client)


@app.route("/viewProjectDetails")
def viewProjectDetails():
    project_id = request.args.get("project_id")
    query = {"_id": ObjectId(project_id)}
    project = project_col.find_one(query)
    return render_template("viewProjectDetails.html", project=project, get_category_id=get_category_id, get_client_id=get_client_id)


@app.route("/viewDeveloperDetails")
def viewDeveloperDetails():
    developer_id = request.args.get("developer_id")
    query = {"_id": ObjectId(developer_id)}
    developer = developer_col.find_one(query)
    return render_template("viewDeveloperDetails.html", developer=developer)


@app.route("/accept_schedule")
def accept_schedule():
    project_id = request.args.get("project_id")
    application_id = request.args.get("application_id")
    query = {'schedule': {"$elemMatch": {"application_id": ObjectId(application_id)}}}
    query1 = {"$set": {"schedule.$.status": status_schedule_accepted}}
    project_col.update_one(query, query1)
    return redirect("/view_schedule?project_id="+str(project_id))


@app.route("/reject_schedule")
def reject_schedule():
    project_id = request.args.get("project_id")
    application_id = request.args.get("application_id")
    query = {'schedule': {"$elemMatch": {"application_id": ObjectId(application_id)}}}
    query1 = {"$set": {"schedule.$.status": status_schedule_rejected}}
    project_col.update_one(query, query1)
    return redirect("/view_schedule?project_id="+str(project_id))


@app.route("/payAmount")
def payAmount():
    project_id = request.args.get("project_id")
    query = {"_id": ObjectId(project_id)}
    project = project_col.find_one(query)
    price = project['project_cost']
    amount = int(price) * 0.1
    application_id = request.args.get("application_id")
    return render_template("payAmount.html", project_id=project_id, application_id=application_id, amount=int(amount))


@app.route("/payAmount1", methods=['post'])
def payAmount1():
    project_id = request.form.get("project_id")
    application_id = request.form.get("application_id")
    amount = request.form.get("amount")
    date = datetime.datetime.now()
    status = status_first_payment
    query = {'$push': {"Payments": {"application_id": ObjectId(application_id), "amount": int(amount), "date": date, "status": status}}}
    project_col.update_one({"_id": ObjectId(project_id)}, query)

    query = {'_id': ObjectId(project_id)}
    query1 = {"$set": {"status": status_Development_Started}}
    project_col.update_one(query, query1)
    return redirect("/view_projects")


@app.route("/pay_remaining_amount")
def pay_remaining_amount():
    project_id = request.args.get("project_id")
    query = {"_id": ObjectId(project_id)}
    project = project_col.find_one(query)
    total_paid_amount = 0
    if 'Payments' in project:
        for payment in project['Payments']:
            total_paid_amount = total_paid_amount + int(payment['amount'])
    remaining_amount = int(project['project_cost']) - int(total_paid_amount)
    application_id = request.args.get("application_id")
    return render_template("pay_remaining_amount.html", remaining_amount=remaining_amount, project_id=project_id, application_id=application_id)


@app.route("/pay_remaining_amount1", methods=['post'])
def pay_remaining_amount1():
    project_id = request.form.get("project_id")
    application_id = request.form.get("application_id")
    amount = request.form.get("remaining_amount")
    print(amount)
    date = datetime.datetime.now()
    status = "Total Amount Paid"
    query = {'$push': {"Payments": {"application_id": ObjectId(application_id), "amount": int(amount), "date": date, "status": status}}}
    project_col.update_one({"_id": ObjectId(project_id)}, query)
    # query = {'Payments': {"$elemMatch": {"application_id": ObjectId(application_id)}}}
    # query1 = {"$set": {"Payments.$.amount": amount, "Payments.$.date": date, "Payments.$.status": status}}
    # project_col.update_one(query, query1)
    return redirect("/view_projects")


@app.route("/view_payments")
def view_payments():
    query = {}
    project_id = request.args.get("project_id")
    if session['role'] == "Client":
        client_id = session['client_id']
        query = {"client_id": ObjectId(client_id)}
    elif session['role'] == "Admin":
        projects = project_col.find()
        projects_ids = []
        for project in projects:
            projects_ids.append({"_id": project['_id']})
            query = {"$or": projects_ids}
    elif session['role'] == "Developer":
        developer_id = session['developer_id']
        query = {"developer_id": ObjectId(developer_id)}
        applications = application_col.find(query)
        application_ids = []
        for application in applications:
            application_ids.append(application['_id'])
            query = {"Payments": {"$elemMatch": {"application_id": {"$in": application_ids}}}}

    projects = project_col.find(query)
    return render_template("view_payments.html", projects=projects, get_client_id=get_client_id, get_developer_id_by_application_payments=get_developer_id_by_application_payments)


def get_developer_id_by_application_payments(application_id):
    query = {"_id": ObjectId(application_id)}
    application = application_col.find_one(query)
    developer_id = application['developer_id']
    query = {"_id": ObjectId(developer_id)}
    developer = developer_col.find_one(query)
    return developer


@app.route("/project_reviews")
def project_reviews():
    project_id = request.args.get("project_id")
    return render_template("project_reviews.html", project_id=project_id)


@app.route("/project_reviews1", methods=['get'])
def project_reviews1():
    query = {}
    project_id = request.args.get("project_id")
    rating = request.args.get('rating')
    review = request.args.get('review')
    date = datetime.datetime.now()
    if session['role'] == "Client":
        review_for = "Developer"
        client_id = session['client_id']
        query = {"project_id": ObjectId(project_id), "status": status_application_accepted}
        application = application_col.find_one(query)
        developer_id = application['developer_id']
        query = {"client_id": ObjectId(client_id), "developer_id": ObjectId(developer_id), "rating": rating, "review": review, "review_for": review_for, "date": date}

    elif session['role'] == "Developer":
        review_for = "Client"
        query = {"project_id": ObjectId(project_id), "status": status_application_accepted}
        application = application_col.find_one(query)
        developer_id = application['developer_id']
        project = project_col.find_one({"_id": ObjectId(project_id)})
        client_id = project['client_id']
        query = {"client_id": ObjectId(client_id), "developer_id": ObjectId(developer_id), "rating": rating, "review": review, "review_for": review_for, "date": date}

    reviews_col.insert_one(query)
    return redirect("/project_reviews?project_id="+str(project_id))


def get_developer_id_by_reviews(developer_id):
    query = {"developer_id": ObjectId(developer_id), "review_for": "Developer"}
    reviews = reviews_col.find(query)
    count = 0
    total_rating = 0
    for review in reviews:
        total_rating = total_rating + int(review['rating'])
        count = count + 1
    if count == 0:
        return ""
    average_rating = total_rating/count
    return average_rating


def get_client_id_by_reviews(client_id):
    query = {"client_id": ObjectId(client_id), "review_for": "Client"}
    reviews = reviews_col.find(query)
    count = 0
    total_rating = 0
    for review in reviews:
        total_rating = total_rating + int(review['rating'])
        count = count + 1
    if count == 0:
        return ""
    average_rating = total_rating/count
    return average_rating


@app.route("/make_as_complete")
def make_as_complete():
    project_id = request.args.get("project_id")
    query = {'_id': ObjectId(project_id)}
    query1 = {"$set": {"status": status_project_completed}}
    project_col.update_one(query, query1)
    query = {"project_id": ObjectId(project_id), "status": status_application_accepted}
    application = application_col.find_one(query)
    application_id = application['_id']
    query = {"_id": ObjectId(application_id)}
    query1 = {"$set": {"status": status_project_completed}}
    application_col.update_one(query, query1)
    query = {'schedule': {"$elemMatch": {"application_id": ObjectId(application_id)}}}
    query1 = {"$set": {"schedule.$.status": status_project_completed}}
    project_col.update_one(query, query1)
    return redirect("/view_projects")


@app.route("/change_developer_password")
def change_developer_password():
    developer_id = request.args.get("developer_id")
    return render_template("change_developer_password.html", developer_id=developer_id)


@app.route("/change_developer_password1", methods=['post'])
def change_developer_password1():
    developer_id = request.form.get("developer_id")
    password = request.form.get("password")
    query = {"_id": ObjectId(developer_id)}
    query1 = {"$set": {"password": password}}
    developer_col.update_one(query, query1)
    return render_template("msg.html", message="Password is Updated", color="text-success")


@app.route("/change_client_password")
def change_client_password():
    client_id = request.args.get("client_id")
    return render_template("change_client_password.html", client_id=client_id)


@app.route("/change_client_password1", methods=['post'])
def change_client_password1():
    client_id = request.form.get("client_id")
    password = request.form.get("password")
    query = {"_id": ObjectId(client_id)}
    query1 = {"$set": {"password": password}}
    client_col.update_one(query, query1)
    return render_template("msg.html", message="Password is Updated", color="text-success")


def is_requested_for_application(application_id):

    query = {"developer_id": ObjectId(session['developer_id']), "status": status_applied_for_project}
    count = application_col.count_documents(query)
    if count == 0:
        return True
    else:
        return False


@app.route("/report")
def report():
    project_id = request.args.get("project_id")
    return render_template("report.html", project_id=project_id)


@app.route("/report1", methods=['post'])
def report1():
    query = {}
    project_id = request.form.get("project_id")
    report_summary = request.form.get("report_summary")
    date = datetime.datetime.now()
    if session['role'] == "Client":
        report_by = "Client"
        status = "Report by Client"
        client_id = session['client_id']
        query = {"project_id": ObjectId(project_id)}
        application = application_col.find_one(query)
        developer_id = application['developer_id']
        query = {"client_id": ObjectId(client_id), "developer_id": ObjectId(developer_id), "report_summary": report_summary, "report_by": report_by, "status": status, "date": date}

    elif session['role'] == "Developer":
        report_by = "Developer"
        status = "Report by Developer"
        developer_id = session['developer_id']
        query = {"_id": ObjectId(project_id)}
        project = project_col.find_one(query)
        client_id = project['client_id']
        query = {"client_id": ObjectId(client_id), "developer_id": ObjectId(developer_id), "report_summary": report_summary, "report_by": report_by, "status": status, "date": date}
    report_col.insert_one(query)
    return render_template("msg.html", message="Reported to Admin", color="text-success")


@app.route("/view_report")
def view_report():
    query = {}
    if session['role'] == "Admin":
        query = {}
    elif session['role'] == "Developer":
        developer_id = session['developer_id']
        query = {"developer_id": ObjectId(developer_id), "report_by": "Developer"}
    elif session['role'] == "Client":
        client_id = session['client_id']
        query = {"client_id": ObjectId(client_id), "report_by": "Client"}
    reports = report_col.find(query)
    reports = list(reports)
    if len(reports) == 0:
        return render_template("msg.html", message="Reports Not Available", color="text-danger")
    return render_template("view_report.html", reports=reports, get_client_id=get_client_id, get_developer_id=get_developer_id)


@app.route("/replay_for_report")
def replay_for_report():
    report_id = request.args.get("report_id")
    return render_template("replay_for_report.html", report_id=report_id)


@app.route("/replay_for_report1", methods=['post'])
def replay_for_report1():
    report_id = request.form.get("report_id")
    report_reply = request.form.get("report_replay")
    query = {"_id": ObjectId(report_id)}
    query1 = {"$set": {"report_replay": report_reply, "status": "Reply by Admin"}}
    report_col.update_one(query, query1)
    return redirect("/view_report")


@app.route("/subscription")
def subscription():
    query = {}
    if session['role'] == "Admin":
        query = {}
    elif session['role'] == "Developer":
        query = {"plan_for": "Developer"}
    elif session['role'] == "Client":
        query = {"plan_for": "Client"}
    subscription_plans = subscription_plan_col.find(query)
    if session['role'] == "Admin":
        query = {}
    elif session['role'] == "Client":
        subscriber_id = session['client_id']
        query = {"subscriber_id": ObjectId(subscriber_id)}
    elif session['role'] == "Developer":
        subscriber_id = session['developer_id']
        query = {"subscriber_id": ObjectId(subscriber_id)}
    subscriptions = subscription_col.find(query)

    return render_template("subscription.html", get_expiry_date=get_expiry_date,  subscription_plans=subscription_plans, get_subscription_plan_id=get_subscription_plan_id, subscriptions=subscriptions, get_client_id_by_subscriber=get_client_id_by_subscriber, get_developer_id_by_subscriber=get_developer_id_by_subscriber)


@app.route("/add_subscription")
def add_subscription():
    return render_template("add_subscription.html")


@app.route("/add_subscription1", methods=['post'])
def add_subscription1():
    validity_days = request.form.get("validity_days")
    plan_price = request.form.get("plan_price")
    plan_for = request.form.get("plan_for")
    query = {"validity_days": validity_days, "plan_price": plan_price, "plan_for": plan_for}
    subscription_plan_col.insert_one(query)
    return redirect("/subscription")


@app.route("/subscribe")
def subscribe():
    subscription_plan_id = request.args.get("subscription_plan_id")
    query = {"_id": ObjectId(subscription_plan_id)}
    subscription_plan = subscription_plan_col.find_one(query)
    plan_price = subscription_plan['plan_price']
    return render_template("subscribe.html", subscription_plan_id=subscription_plan_id, plan_price=plan_price)


@app.route("/subscribe1", methods=['post'])
def subscribe1():
    query = {}
    subscription_plan_id = request.form.get("subscription_plan_id")
    query = {"_id": ObjectId(subscription_plan_id)}
    subscription_plan = subscription_plan_col.find_one(query)
    validity_days = int(subscription_plan['validity_days'])
    status = "Subscription Amount Paid"
    date = datetime.datetime.now()
    expiry_date = date + datetime.timedelta(days=validity_days)
    # date = date.replace('T', ' ')
    # date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    if session['role'] == "Client":
        client_id = session['client_id']
        subscriber = "Client"
        query = {"subscription_plan_id": ObjectId(subscription_plan_id), "subscriber_id": ObjectId(client_id), "expiry_date": expiry_date, "status": status, "date": date, "subscriber": subscriber}
    elif session['role'] == "Developer":
        developer_id = session['developer_id']
        subscriber = "Developer"
        query = {"subscription_plan_id": ObjectId(subscription_plan_id), "subscriber_id": ObjectId(developer_id), "expiry_date": expiry_date, "status": status, "date": date, "subscriber": subscriber}
    subscription_col.insert_one(query)
    return render_template("msg.html", message="Amount Paid Successfully", color="text-success")


def get_subscription_plan_id(subscription_plan_id):
    query = {"_id": ObjectId(subscription_plan_id)}
    subscription_plan = subscription_plan_col.find_one(query)
    return subscription_plan


def get_client_id_by_subscriber(subscriber_id):
    query = {"_id": ObjectId(session['client_id'])}
    client = client_col.find_one(query)
    return client


def get_developer_id_by_subscriber(subscriber_id):
    query = {"_id": ObjectId(session['developer_id'])}
    developer = client_col.find_one(query)
    return developer


def get_expiry_date(subscription_plan_id):
    query = {}
    if session['role'] == "Client":
        subscriber_id = session['client_id']
        query = {"subscriber_id": ObjectId(subscriber_id)}
    elif session['role'] == "Developer":
        subscriber_id = session['developer_id']
        query = {"subscriber_id": ObjectId(subscriber_id)}
    subscriptions = subscription_col.find(query)
    for subscription in subscriptions:
        expiry_date = subscription['expiry_date']
        today = datetime.datetime.now()
        if today <= expiry_date:
            return False
    else:
        return True


# @app.route("/message")
# def message():
#     project_id = request.args.get("project_id")
#     if session['role'] == "Client":
#         query = {"project_id": ObjectId(project_id)}
#         application = application_col.find_one(query)
#         developer_id = application['developer_id']
#         query = {"_id": ObjectId(developer_id)}
#         developer = developer_col.find_one(query)
#         return render_template("message.html", project_id=project_id, developer=developer)
#     elif session['role'] == "Developer":
#         query = {"_id": ObjectId(project_id)}
#         project = project_col.find_one(query)
#         client_id = project['client_id']
#         query = {"_id": ObjectId(client_id)}
#         client = client_col.find_one(query)
#         return render_template("message.html", project_id=project_id, client=client)


@app.route("/get_messages")
def get_messages():
    query = {}
    receiver_id = request.args.get('receiver_id')
    if session['role'] == "Client":
        sender_id = session['client_id']
        query = {"$or": [{"sender_id": ObjectId(sender_id), "receiver_id": ObjectId(receiver_id)}, {"sender_id": ObjectId(receiver_id), "receiver_id": ObjectId(sender_id)}]}
    elif session['role'] == "Developer":
        sender_id = session['developer_id']
        query = {"$or": [{"sender_id": ObjectId(sender_id), "receiver_id": ObjectId(receiver_id)},{"sender_id": ObjectId(receiver_id), "receiver_id": ObjectId(sender_id)}]}
    messages = chat_col.find(query)
    messages2 = []
    for message in messages:
        message['_id'] = str(message['_id'])
        message['sender_id'] = str(message['sender_id'])
        message['receiver_id'] = str(message['receiver_id'])
        messages2.append(message)

    return {"messages": messages2}


@app.route("/get_message")
def get_message():
    query = {}
    receiver_id = request.args.get('receiver_id')
    if session['role'] == "Client":
        sender_id = session['client_id']
        query = {"$or": [{"sender_id": ObjectId(sender_id), "receiver_id": ObjectId(receiver_id), "isSenderRead": "unread"}, {"sender_id": ObjectId(receiver_id), "receiver_id": ObjectId(sender_id), "isSenderRead": "unread"}]}
    elif session['role'] == "Developer":
        sender_id = session['developer_id']
        query = {"$or": [{"sender_id": ObjectId(sender_id), "receiver_id": ObjectId(receiver_id), "isSenderRead": "unread"}, {"sender_id": ObjectId(receiver_id), "receiver_id": ObjectId(sender_id), "isSenderRead": "unread"}]}
    messages = chat_col.find(query)
    messages = list(messages)
    for message in messages:
        if str(message['sender_id']) == sender_id:
            query = {"_id": message['_id']}
            query2 = {"$set": {"isSenderRead": 'read'}}
            chat_col.update_one(query, query2)
        elif str(message['receiver_id']) == sender_id:
            query = {"_id": message['_id']}
            query2 = {"$set": {"isReceiverRead": 'read'}}
            chat_col.update_one(query, query2)
    messages2 = []
    for message in messages:
        message['_id'] = str(message['_id'])
        message['sender_id'] = str(message['sender_id'])
        message['receiver_id'] = str(message['receiver_id'])
        messages2.append(message)
    return {"messages": messages2}


@app.route("/send_messages")
def send_messages():
    receiver_id = request.args.get('receiver_id')
    if session['role'] == "Client":
        sender_id = session['client_id']
    elif session['role'] == "Developer":
        sender_id = session['developer_id']
    message = request.args.get('message')
    query = {"sender_id": ObjectId(sender_id), "receiver_id": ObjectId(receiver_id), "message": message,"isSenderRead":'unread', "isReceiverRead":'read', "date": str(datetime.datetime.now())}
    chat_col.insert_one(query)
    return {"status": "ok"}


@app.route("/set_as_read_receiver")
def set_as_read_receiver():
    receiver_id = request.args.get('receiver_id')
    if session['role'] == "Client":
        sender_id = session['client_id']
    elif session['role'] == "Developer":
        sender_id = session['developer_id']
    query = {"sender_id": ObjectId(receiver_id), "receiver_id": ObjectId(sender_id)}
    query2 = {"$set":{"isReceiverRead": "read"}}
    chat_col.update_one(query, query2)
    return {"status": "ok"}


@app.route("/set_as_read_sender")
def set_as_read_sender():
    receiver_id = request.args.get('receiver_id')
    if session['role'] == "Client":
        sender_id = session['client_id']
    elif session['role'] == "Developer":
        sender_id = session['developer_id']
    query = {"sender_id": ObjectId(receiver_id), "receiver_id": ObjectId(sender_id)}
    query2 = {"$set": {"isSenderRead": "read"} }
    chat_col.update_one(query, query2)
    return {"status": "ok"}


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


app.run(debug=True)
