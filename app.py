from flask import Flask, render_template, request,redirect, jsonify,session, url_for, flash
from utils.gemini_helper import detect_issue
from database.db import get_conn
from flask_session import Session
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
app.secret_key='kishore@07#'
Session(app)

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)


@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template("chat.html")

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method=="POST":

        username=request.form["username"]
        email=request.form["email"]
        password=generate_password_hash(request.form["password"])

        conn=get_conn()
        cur=conn.cursor()

        cur.execute(
        "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
        (username,email,password))

        conn.commit()

        return redirect("/login")

    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        conn=get_conn()
        cur=conn.cursor()

        cur.execute("SELECT id,password FROM users WHERE email=%s",(email,))
        user=cur.fetchone()

        if user and check_password_hash(user[1],password):

            session["user"]=user[0]
            return redirect("/")
        flash("Invalid email or password", "error")
        return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

'''
@app.route("/ask", methods=["POST"])
def ask():
    # 1. Get message safely
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"reply": "Invalid request"}), 400

    msg = data["message"]
    

    # 2. Get category from Gemini
    category = detect_issue(msg)
    
    # 3. Handle the "UNKNOWN" or error case
    if category == "UNKNOWN":
        return jsonify({"reply": "I'm having trouble connecting to my brain. Please try again later!"})

    # 4. Database Lookup
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT steps FROM solutions WHERE issue=%s",
            (category,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return jsonify({"reply": row[0]})
        else:
            return jsonify({"reply": f"I recognized this as a {category} issue, but I don't have a specific solution in my database yet."})
            
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({"reply": "Internal database error."}), 500 '''

from flask_caching import Cache

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    print(data)

    # Normalize input to save cache space
    msg = data.get("message", "").lower().strip() 

    # 1. Check cache
    category = cache.get(msg)
    
    # 2. If not in cache, call Gemini
    if not category:
        category = detect_issue(msg)
        cache.set(msg, category, timeout=3600)
    

    # 3. Handle Responses
    if category == "GREETING":
        return jsonify({"reply": "Hello! I'm your Tech Support bot. How can I help with your laptop today?"})

    if category == "UNKNOWN":
        return jsonify({"reply": "I'm sorry, I couldn't quite understand that."})
    
    if category.lower() in ["ok", "okay", "fine", "thanks"]:
        return jsonify({"reply": "It's ok! Have a nice day"})

    # 4. Database Lookup
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT steps FROM solutions WHERE issue=%s", (category,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return jsonify({"reply": row[0]})
        else:
            return jsonify({"reply": f"It sounds like a {category} issue, but I don't have a fix for that yet."})
    except Exception as e:
        return jsonify({"reply": "Database connection error."})



@app.route("/ticket", methods=["POST"])
def ticket():

    msg = request.json["problem"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tickets(problem,status) VALUES(%s,'OPEN')",
        (msg,)
    )

    conn.commit()

    return jsonify({"msg":"Ticket created"})


app.run(debug=True)