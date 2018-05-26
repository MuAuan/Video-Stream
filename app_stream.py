#!/usr/bin/env python                                                                      
# -*- coding: utf-8 -*-                                                                   
from flask import Flask, stream_with_context, request, Response, flash
from flask import render_template, redirect
from time import sleep                                                                     

app = Flask(__name__)                                                                     

@app.route('/')
def index():
    return redirect('/stream')  #render_template('template.html')

def stream_template(template_name, **context):                                             
    app.update_template_context(context)                                                   
    t = app.jinja_env.get_template(template_name)                                          
    rv = t.stream(context)
    rv.disable_buffering()
    return rv

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]                                                     
def generate():                                                                           
    for item in data:                                                                      
        yield str(item)                                                                   
        sleep(1)                                                                           
        
@app.route('/stream')                                                                       
def stream_view():
    rows = generate()
    return Response(stream_with_context(stream_template('template.html', rows=rows)))

if __name__ == '__main__':                                                                   
    app.debug = True                                                                         
    app.run()