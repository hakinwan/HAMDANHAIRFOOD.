import json
from datetime import date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)


app = Flask(__name__)
app.secret_key = "hamdan-hair-food-key"

ADMIN_PASSWORD = "wande0189"


# MY PRODUCT PRICES

price_50g = 600
price_100g = 1100


# LOAD SAVED DATA FROM JSON FILE

with open("data.json", "r") as f:
    data = json.load(f)

stock_50g = data["stock_50g"]
stock_100g = data["stock_100g"]

orders = data["orders"]
sales = data["sales"]


# FUNCTION TO SAVE DATA TO JSON FILE

def save_data():
    data = {
        "stock_50g": stock_50g,
        "stock_100g": stock_100g,
        "orders": orders,
        "sales": sales
    }

    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


# WELCOME PAGE

@app.route("/")
def home():
    return render_template("index.html")


# SHOP PAGE

@app.route("/shop")
def shop():
    return render_template(
        "shop.html",
        stock_50g=stock_50g,
        stock_100g=stock_100g
    )


# ADMIN LOGIN

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("Login successful!")
            return redirect(url_for("admin_dashboard"))

        flash("Incorrect password.")

    return render_template("admin_login.html")


# ADMIN DASHBOARD

@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("admin_login"))

    return render_template(
        "admin_dashboard.html",
        stock_50g=stock_50g,
        stock_100g=stock_100g
    )


# ADMIN LOGOUT

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    flash("You have logged out.")

    return redirect(url_for("admin_login"))

# RESTOCK PRODUCTS


@app.route("/restock", methods=["GET", "POST"])
def restock():

    global stock_50g, stock_100g

    # CHECK ADMIN LOGIN
    if not session.get("admin_logged_in"):
        flash("Please log in as admin first.")
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        size = request.form.get("size", "")
        quantity_text = request.form.get("quantity", "")

        # VALIDATE QUANTITY
        try:
            quantity = int(quantity_text)

            if quantity <= 0:
                flash("Quantity must be greater than zero.")
                return redirect(url_for("restock"))

        except ValueError:
            flash("Please enter a valid whole number.")
            return redirect(url_for("restock"))

        # ADD NEW STOCK
        if size == "50g":
            stock_50g += quantity

        elif size == "100g":
            stock_100g += quantity

        else:
            flash("Invalid product size.")
            return redirect(url_for("restock"))

        # SAVE UPDATED DATA
        save_data()

        flash(
            f"Restocking successful! Added {quantity} "
            f"containers of the {size} product."
        )

        return redirect(url_for("restock"))

    return render_template(
        "restock.html",
        stock_50g=stock_50g,
        stock_100g=stock_100g
    )
# PLACE AN ORDER

@app.route("/place_order", methods=["POST"])
def place_order():
    global stock_50g, stock_100g

    size = request.form.get("size", "")
    quantity_text = request.form.get("quantity", "")

# VALIDATE QUANTITY

    try:
        quantity = int(quantity_text)

        if quantity <= 0:
            flash("Quantity must be greater than zero.")
            return redirect(url_for("shop"))

    except ValueError:
        flash("Please enter a valid whole number.")
        return redirect(url_for("shop"))

# CHECK PRODUCT SIZE AND STOCK

    if size == "50g":
        price = price_50g

        if quantity > stock_50g:
            flash("Sorry, there is not enough 50g stock.")
            return redirect(url_for("shop"))

        stock_50g -= quantity

    elif size == "100g":
        price = price_100g

        if quantity > stock_100g:
            flash("Sorry, there is not enough 100g stock.")
            return redirect(url_for("shop"))

        stock_100g -= quantity

    else:
        flash("Invalid product size.")
        return redirect(url_for("shop"))

    # CALCULATE TOTAL PRICE

    total_price = quantity * price

# RECORD CUSTOMER ORDER

    orders.append({
        "size": size,
        "quantity": quantity,
        "total": total_price
    })


# RECORD SALE

    sales.append({
        "size": size,
        "quantity": quantity,
        "amount": total_price,
        "date": str(date.today())
    })


# SAVE UPDATED DATA

    save_data()

    flash(
        f"Order successful! You ordered {quantity} "
        f"container(s) of the {size} size. "
        f"Total price: ₦{total_price:,}."
    )

    return redirect(url_for("shop"))


# START THE WEBSITE

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)