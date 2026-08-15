import os
import sys

# Add app/ to sys.path so app modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from app import app  # noqa: E402

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
