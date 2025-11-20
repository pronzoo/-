from flask import Blueprint, render_template

users= Blueprint("users", __name__)

@users.route("/")
def list_users():
    fake_users = ["Santi", "pronzito" , "Inge"]
    return render_template("usuarios.html", users=fake_users)