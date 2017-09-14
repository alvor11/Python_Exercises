from cs50 import sql
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application\Настроить приложение
app = Flask(__name__)

# ensure responses aren't cached\Обеспечить, чтобы ответы не кэшировались
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter\Настраиваемый фильтр
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)\Настроить сеанс для использования файловой системы (вместо подписанных файлов cookie)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database\Настроить библиотеку CS50 на использование базы данных SQLite
db = sql.SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    # Get current cash ballance fro current user
    cash = db.execute("select cash from users where id = :id", id=session["user_id"])
    cashBal = cash[0]['cash']
    portTotal = cash[0]['cash']
    # Get stock portfolio for user and display with totals
    data=[]
    portfolio = db.execute('select * from portfolio where owner_id = :owner_id order by symbol', owner_id=session['user_id'])
    for record in portfolio:
        share = lookup(record['symbol'])
        symbol = share['symbol']
        name = share['name']
        shares = record['shares']
        price = share['price']
        shareTotal = shares * price
        portTotal += shareTotal
        price = usd(price)
        total = usd(shareTotal)
        # List Data values
        lst=[symbol, name, shares, price, total]
        # List Key names
        keys=['Symbol','Name','Shares','Price','Total']
        # Build list of dictionaries
        data.append(dict(zip(keys, lst)))
    cashBal = usd(cashBal)
    total = usd(portTotal)
    return render_template('index.html', cashBal=cashBal, total=total, data=data)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "GET":
       
        return render_template("buy.html")
    if request.method == "POST":
        current_user = int(session["user_id"])
        # проверка ввода
        if not request.form['symbol'] or not request.form['shares'] or int(request.form['shares']) < 0:
            return apology("not wright input")
    
        # текущий остаток денег
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id=current_user)

        stock = lookup(request.form['symbol'])
        if stock:
            numShares = int(request.form['shares'])
            purchase = numShares * stock['price']
            if purchase > cash[0]['cash']:
                return apology("you have not many money")
            else:
                cashBal = cash[0]['cash'] - purchase
                db.execute("INSERT INTO trans (tran_type, owner_id, symbol, shares, price) VALUES(:tran_type, :owner_id, :symbol, :shares, :price)", tran_type='buy', owner_id=current_user, symbol=stock['symbol'], shares=numShares, price=purchase)
                db.execute("UPDATE users SET cash = :cashBal WHERE id = :id", cashBal=cashBal, id=current_user)
                current_shares = db.execute("SELECT id, shares FROM portfolio WHERE owner_id = :id and symbol = :symbol", id=current_user, symbol=stock['symbol'])
                if current_shares:
                    newShares = current_shares[0]['shares'] + numShares
                    db.execute("UPDATE portfolio SET shares = :newShares WHERE id = :id", newShares=newShares, id=current_shares[0]['id'])
                else:
                    db.execute("INSERT INTO portfolio (owner_id, symbol, shares) VALUES(:owner_id, :symbol, :shares)", owner_id=current_user, symbol=stock['symbol'], shares=numShares)
        else:
            return apology("Stock Symbol not found")
            
        return redirect(url_for("index"))


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    data = []
    log = db.execute("SELECT * FROM trans WHERE owner_id = :owner_id", owner_id=session['user_id'])
    for row in log:
        tran = row['tran_type']
        symbol = row['symbol']
        price = usd(row['price'])
        shares = row['shares']
        date = row['date']
        # List Data values
        lst=[tran, symbol, price, shares, date]
        # List Key names
        keys=['Transaction', 'Symbol', 'Price', 'Shares', 'Date']
        # Build list of dictionaries
        data.append(dict(zip(keys, lst)))
    return render_template('history.html', data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id\Забыть любой user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)\Если пользователь достиг маршрута через POST (например, отправив форму через POST)
    if request.method == "POST":

        # ensure username was submitted\Обеспечить, чтобы имя пользователя было отправлено
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username/Запрашивать базу данных для имени пользователя
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct/Убедитесь, что имя пользователя существует, и пароль правильный
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in/Помните, какой пользователь вошел в систему
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)\Иначе, если пользователь достигнет маршрута через GET (как, нажав ссылку или перенаправляя)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        # запрос по акциям
        if request.form.get("symbol") == "" or request.form.get("symbol").startswith("^") or "," in request.form.get("symbol"):
            return apology("Error")
        
        data = lookup(request.form.get("symbol"))
        if not data:
            return apology(request.form.get("symbol") + " not found")
       
        return render_template("quoted.html", data=data)
    else:
        return apology("Method not supported")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user.""" 


    # forget any user_id\Забыть любой user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)\Если пользователь достиг маршрута через POST (например, отправив форму через POST)
    if request.method == "POST":

        # ensure username was submitted\Обеспечить, чтобы имя пользователя было отправлено
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        
        elif request.form.get("password") != request.form.get("confirm password"):
            return apology("don`t confirm password")

        # query database for username/Добавляем в базу данных  нового пользователя
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # Проверка уникальности имени
        if len(rows) != 0:
            return apology("this name was registered. Input over name")
        
        hash = pwd_context.hash(request.form.get("password"))
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=hash)
        if not rows: 
            return apology("Dont register(")
        # remember which user has logged in/Помните, какой пользователь вошел в систему
        session["user_id"] = rows

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)\Иначе, если пользователь достигнет маршрута через GET (как, нажав ссылку или перенаправляя)
    else:
        return render_template("register.html")

    #return apology("TODO")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "GET":
        return render_template("sell.html")
    if request.method == "POST":
        if not request.form['symbol']:
            return apology("Error")
        # get balans
        cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session['user_id'])
        cashBal = cash[0]['cash']
        
        portfolio = db.execute("SELECT * FROM portfolio WHERE owner_id = :owner_id and symbol = :symbol", owner_id=session['user_id'], symbol=request.form['symbol'].upper())
        if not portfolio:
            return apology("Error")
        
        data = lookup(request.form['symbol'])
        
        market_price = data['price']
        shares = portfolio[0]['shares']
        proceeds = shares * market_price
       
        db.execute("DELETE FROM portfolio WHERE id = :id", id=portfolio[0]['id'])
        
        db.execute("INSERT INTO trans (tran_type, owner_id, symbol, shares, price) VALUES(:tran_type, :owner_id, :symbol, :shares, :price)", tran_type='sell', owner_id=session['user_id'], symbol=data['symbol'], shares=shares, price=proceeds)
        cashBal += proceeds
        
        db.execute("UPDATE users SET cash=:cashBal WHERE id=:id", cashBal=cashBal, id=session['user_id'])
        
        return redirect(url_for("index"))
