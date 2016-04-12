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
            if self.path.endswith("/") or self.path.endswith("catalog/"):
                categories = session.query(Category).all()
                output = ""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for category in categories:
                    output += category.name
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output)
                return
            else:
                self.send_error(404, 'File Not Found: %s' % self.path)
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print 'Web server running...open localhost:8080/restaurants in your browser'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
