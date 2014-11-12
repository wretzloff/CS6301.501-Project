# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))

def test():
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_login()
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


auth.settings.allow_basic_login = True
@auth.requires_login()
@request.restful()
def api():
    session.forget()
    def GET(table,id='all'):
        if table == 'messages':
            if str(id.lower()) == 'all':
                #get all messages
                return 'This is all messages'
            else:
                #get message by id
                return 'This is all message with id %s' % id
        elif table == 'contacts':
            #get all contacts
            return 'This is all contacts'
    def POST(*args,**vars):
        message = 'DEFAULT'
        target = 'TARGET'
        if len(args) > 0:
            if 'send' == args[0]:
                message = args[1]
                target = args[2]
        elif vars['type'] == 'send':
            message = vars['message']
            target = vars['to']
        return 'You have posted to "%s" a message that says: "%s"' % (target, message)
    def PUT(*args,**vars):
        return ''
    def DELETE(table,id):
        if table == 'messages':
            return 'You have deleted message %s' % id
        return 'invalid'
    return locals()
