from app import create_app

app = create_app()
app.debug = True
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
