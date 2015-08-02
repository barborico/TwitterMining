# AUTHOR Brynn Arborico
# DATE July 24, 2015
# COMPANY Upstream Health

# NAME Web Deployment of Twitter-Mining App

# SOURCES Used code from digitalmihailo.com

import web
from web import form

from TwitterStreaming import *

render = web.template.render('templates/')
urls = ('/', 'index')
app = web.application(urls, globals())

# form for entering a geobox to filter tweets by region
getRegion = form.Form(
    form.Textbox("north",
                 form.notnull,
                 form.regexp('-?\d+', ' Must be a number.'),
                 form.Validator(" Must be between 90 and -90.",
                                lambda n: 90 >= int(n) >= -90),
                 description='Northern: ',
                 value="90"),
    form.Textbox("south",
                 form.notnull,
                 form.regexp('-?\d+', ' Must be a number.'),
                 form.Validator(" Must be between 180 and -180.",
                                lambda n: 90 >= int(n) >= -90),
                 description='Southern: ',
                 value="-90"),
    form.Textbox("east",
                 form.notnull,
                 form.regexp('-?\d+', ' Must be a number.'),
                 form.Validator(" Must be between 180 and -180.",
                                lambda n: 180 >= int(n) >= -180),
                 description='Eastern: ',
                 value="180"),
    form.Textbox("west",
                 form.notnull,
                 form.regexp('-?\d+', ' Must be a number.'),
                 form.Validator(" Must be between 180 and -180.",
                                lambda n: 180 >= int(n) >= -180),
                 description='Western: ',
                 value="-180"),
    validators = [form.Validator("Invalid north/south boundaries.",
                                 lambda f: int(f.north) > int(f.south)),
                  form.Validator("Invalid east/west boundaries.",
                                 lambda f: int(f.east) > int(f.west))]
    )

# form for entering terms to include or exclude from tweets
getTerms = form.Form(
    form.Textarea("include"),
    form.Textarea("exclude")
    )

class index:
    '''home page of the web app'''
    
    includeTerms = ""
    excludeTerms = ""
    geobox = [-180, -90, 180, 90]

    stream = ""
    
    def GET(self):
        '''Presents home page to user (response to HTTP Get request)'''
        
        i = web.input(streaming=False)
        streaming = i.streaming

        regionForm = getRegion()
        termsForm = getTerms()
        
        return render.MiningWebpage(regionForm, termsForm, self.stream)
    
    def POST(self):
        '''Takes inputs on home page from user (response to HTTP Post request)'''
        
        i = web.input(streaming=False)
        streaming = i.streaming

        regionForm = getRegion()
        termsForm = getTerms()
        
        if regionForm.validates() and termsForm.validates():
            self.includeTerms = termsForm["include"].value.encode('ascii')
            self.excludeTerms = termsForm["exclude"].value.encode('ascii')
            self.geobox = [int(regionForm["west"].value),
                          int(regionForm["south"].value),
                          int(regionForm["east"].value),
                          int(regionForm["north"].value)]

        if streaming:
            self.stream = streamTweets(self.geobox, self.includeTerms, self.excludeTerms)

        return render.MiningWebpage(regionForm, termsForm, self.stream)

 
if __name__ == "__main__":  
    app.run()
