# Project 3 - "Sports Catalog"
## Udacity's Full Stack Developer Nanodegree

## Instructions:
* Start vagrant virtual machine by navigating to `vagrant` directory and then
typing `vagrant up` in your terminal
* Log into the virtual machine by typing `vagrant ssh`
* Navigate to the code found in `/vagrant/catalog`
* Run `webserver.py` to start the server
* Run `catalog.py` to create the (empty) catalog database which will create
`catalog.db`
* The web app will run at 'localhost:8000/catalog' (not in the VM)

### Things to Note
* The default address can be changed at the bottom of `webserver.py` in the
method `app.run`
* The `client_secrets.json` file has been provided but you can use your own by
downloading your own `client_secrets.json` from your Google Developer account.
You will have to add create your own application with the proper "redirect uris"
and proper "javascript origins". You also will have to use your client id in
`login.html` under `data-clientid` in the Google+ sign-in button.
