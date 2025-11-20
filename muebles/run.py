from app import create_app

app = create_app() #llamamos a la funcon de create app para instanciar la aplicacion

if __name__ == "__main__":
    app.run(debug=True)