import datetime
import urllib.parse
import yaml

footerString = '{% include profileHTML %}'
ghBase = 'https://github.com/BioSchemas/specifications/'
ghTasksBase = ghBase + 'labels/type%3A%20'
ghExamplesBase = ghBase + 'tree/master/'

def profileHeader(profileName, profileDescription, version, status, groupName, hasLiveDeploy):
    header_properties = {}
    header_properties['name'] = profileName
    header_properties['description'] = profileDescription
    header_properties['version'] = version
    header_properties['version_date'] = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    header_properties['status'] = status
    header_properties['spec_type'] = 'Profile'
    header_properties['group'] = groupName
    header_properties['use_cases_url'] = '/useCases/' + profileName + '/'
    header_properties['gh_tasks'] = ghTasksBase + urllib.parse.quote(profileName)
    if hasLiveDeploy:
        header_properties['live_deploy'] = '/liveDeploys/'
    header_properties['full_example'] = ghExamplesBase + profileName + '/examples/' + version
    return yaml.dump(header_properties)

description = '''A guide for how to describe datasets in the life-sciences using Schema.org-like
    annotation.'''
version = '0.3'
profileString = profileHeader('Dataset', description, version, 'revision', 'data', True)
print(profileString + footerString)
