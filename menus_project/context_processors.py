from .constants import PROJECT_NAME

def project_name(request):
    return {'project_name': PROJECT_NAME}
