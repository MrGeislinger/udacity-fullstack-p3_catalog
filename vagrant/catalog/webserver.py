from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from catalog import Base, Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Allow for the stylesheet
            if self.path.endswith('styles.css'):
                categories = session.query(Category).all()
                with open('website_template/styles.css','r') as stylesheet:
                    output = stylesheet.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                self.wfile.write(output)
                return

            # Home page
            if self.path.endswith('/') or self.path.endswith('catalog/'):
                categories = session.query(Category).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # Find categories
                output_categories = []
                for category in categories:
                    output_categories.append('<h3>%s</h3>' %category.name)
                all_categories = ''.join(output_categories)
                # Find recent items
                output_recent_items = []
                all_recent_items = ''.join(output_recent_items)
                # TODO(VictorLoren): Read in recent items
                # Read in HTML template and replace parts
                with open('website_template/index.html','r') as html_file:
                    output = html_file.read()\
                             .replace('%CATEGORIES', all_categories)\
                             .replace('%RECENT_ITEMS', all_recent_items)


                self.wfile.write(output)
                return
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


def main():
    try:
        server = HTTPServer(('', 8000), webServerHandler)
        print 'Web server running...open localhost:8000/ in your browser'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
