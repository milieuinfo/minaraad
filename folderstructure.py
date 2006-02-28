"""Folderstructure contains the folder structure previously
contained in 'AppConfig.py'. That file got too big, so it got
factored out.
"""

VOORSTELLING_CHILDREN = [
    {'id':'taakstelling', 
     'title':'Taakstelling', 
     'type':'Document',
     'children':[]},
    {'id':'werking', 
     'title':'Werking', 
     'type':'Document',
     'children':[]},
    {'id':'grafieken', 
     'title':'Grafieken', 
     'type':'Document',
     'children':[]},
    {'id':'samenstelling', 
     'title':'Samenstelling',
     'type':'Document',
     'children':[]},
    {'id':'personeel',
     'title':'Personeel',
     'type':'Document',
     'children':[]},
    {'id':'plattegrond',
     'title':'Plattegrond',
     'type':'Document',
     'children':[]},
    {'id':'internemilieu_enerziezorg', 
     'title':'Interne milieu- en enerziezorg',
     'type':'Document',
     'children':[]},]

NIEUWSBRIEVEN_CHILDREN = [
    {'id':'newsl_2006', 
     'title':'2006', 
     'type':'Folder',
     'children':[]},
    {'id':'newsl_2005', 
     'title':'2005', 
     'type':'Folder',
     'children':[]},
    {'id':'newsl_2004', 
     'title':'2004', 
     'type':'Folder',
     'children':[]},
    {'id':'newsl_2003', 
     'title':'2003', 
     'type':'Folder',
     'children':[]},]

PERSBERICHTEN_CHILDREN = [
    {'id':'pressr_2006', 
     'title':'2006', 
     'type':'Folder',
     'children':[]},
    {'id':'pressr_2005', 
     'title':'2005', 
     'type':'Folder',
     'children':[]},
    {'id':'pressr_2004', 
     'title':'2004', 
     'type':'Folder',
     'children':[]},
    {'id':'pressr_2003', 
     'title':'2003', 
     'type':'Folder',
     'children':[]},
    {'id':'pressr_2002', 
     'title':'2002', 
     'type':'Folder',
     'children':[]},]

ADVIEZEN_CHILDREN = [
    {'id':'adv_2006', 
     'title':'2006', 
     'type':'Folder',
     'children':[]},
    {'id':'adv_2005', 
     'title':'2005', 
     'type':'Folder',
     'children':[]},
    {'id':'adv_2004', 
     'title':'2004', 
     'type':'Folder',
     'children':[]},
    {'id':'adv_2003', 
     'title':'2003', 
     'type':'Folder',
     'children':[]},
    {'id':'adv_2002', 
     'title':'2002', 
     'type':'Folder',
     'children':[]},
    {'id':'adv_2001', 
     'title':'2001', 
     'type':'Folder',
     'children':[]},
    {'id':'adv_1999', 
     'title':'1999', 
     'type':'Folder',
     'children':[]},]



ROOT_CHILDREN = [
    {'id':'voorstelling', 
     'title':'Voorstelling', 
     'type':'Folder',
     'children':VOORSTELLING_CHILDREN},
    {'id':'adviezen', 
     'title':'Adviezen', 
     'type':'Folder',
     'children':ADVIEZEN_CHILDREN},
    {'id':'jaarverslag', 
     'title':'Jaarverslag', 
     'type':'Folder',
     'children':[]},
    {'id':'nieuwsbrieven', 
     'title':'Nieuwsbrieven', 
     'type':'Folder',
     'children':NIEUWSBRIEVEN_CHILDREN},
    {'id':'persberichten', 
     'title':'Persberichten', 
     'type':'Folder',
     'children':PERSBERICHTEN_CHILDREN},
    {'id':'studies', 
     'title':'Studies', 
     'type':'Folder',
     'children':[]},
    {'id':'hoorzittingen', 
     'title':'Hoorzittingen', 
     'type':'Folder',
     'children':[]},
    {'id':'evenementen', 
     'title':'Evenementen', 
     'type':'Folder',
     'children':[]},
    {'id':'contactpersonen', 
     'title':'Contactpersonen', 
     'type':'Folder',
     'children':[]},]
