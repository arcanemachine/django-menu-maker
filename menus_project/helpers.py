from menus_project.urls import apps

def get_url(app_name: str, view_name: str) -> str:

    if not type(app_name) == str:
        raise TypeError("app_name must be a string")
    elif not type(view_name) == str:
        raise TypeError("view_name must be a string")
    elif app_name not in apps:
        raise ValueError("app_name not found in project.urls.apps")

    return 'Hello'


    
