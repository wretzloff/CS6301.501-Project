# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

@auth.requires_login()
def index():
    response.title = "Inbox for " + auth.user.email
    return dict()

def compose():
    response.title = "Compose message"
    form=FORM('To:', INPUT(_name='toField',requires=IS_NOT_EMPTY()), 
		TEXTAREA(_name='messageField',requires=IS_NOT_EMPTY()), 
		INPUT(_type='submit', _value="Send"))
    if form.accepts(request,session):
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(formToDisplay=form)

def teamA():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))


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
    def GET(table,message_id='all'):
        if table == 'messages':
            if message_id.lower() == 'all':
                user_id = auth.user.id
                message_list = []
                for user_row in db(db.auth_user.id == user_id).select():
                    for message_row in user_row.messages.select():
                        message_list.append('%s: %s' % (message_row.id, message_row.email_text))
                return 'This is all messages: %s' % message_list
            else:
                try:
                    message_id = int(message_id)
                except:
                    return 'FAIL! ID not an integer.'
                user_id = auth.user.id
                message = ''
                for user_row in db(db.auth_user.id == user_id).select():
                    for message_row in user_row.messages.select():
                        if message_row.id == message_id:
                            message = message_row.email_text
                if message == '':
                    return 'FAIL! Message id not found.'
                else:
                    return '%s: %s' % (message_id, message)
        elif table == 'contacts':
            contacts = []
            for row in db().select(db.auth_user.email):
                contacts.append(row.email)
            return 'This is all contacts: %s' % contacts
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
        if message == '' or message == 'DEFAULT':
            return 'FAIL! Invalid message.'
        else:
            try:
                row = db(db.auth_user.email == target).select(db.auth_user.id)
            except:
                return 'FAIL! Error at getting target user.'
            if len(row) == 0:
                return 'FAIL! Target %s not found.' % target
            else:
                target_id = row[0].id
                user_id = auth.user.id
                db.messages.insert(to_user=target_id, from_user=user_id, email_text=message)
            return 'You have posted to "%s" a message that says: "%s"' % (target, message)
    def PUT(*args,**vars):
        return ''
    def DELETE(table,message_id):
        if table == 'messages':
            try:
                message_id = int(message_id)
            except:
                return 'FAIL! ID not an integer.'
            db(db.messages.id == message_id).delete()
            return 'You have deleted message %s' % message_id
        return 'invalid'
    return locals()




#----- SSL ---------------
def generate_ssl_key():
    import os
    cert_dir, CERT_FILE, KEY_FILE = (os.path.join(request.folder, "private"), 'mysite.crt', 'mysite.key')
    return(dict(cert_dir=cert_dir, CERT_FILE=CERT_FILE, KEY_FILE=KEY_FILE))
