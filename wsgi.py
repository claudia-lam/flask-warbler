# wsgi.py
# Set the path
from application import create_app
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


app = create_app()

if __name__ == "__main__":
    app.run()
