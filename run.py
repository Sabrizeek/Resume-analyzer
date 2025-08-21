# run.py

from project import create_app

app = create_app()

if __name__ == '__main__':
    # Use debug=False in a production environment
    app.run(debug=True)