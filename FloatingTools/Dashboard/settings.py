# FloatingTools imports
import FloatingTools

# flask imports
from flask import request, render_template, redirect

# package imports
from utilities import SERVER


@SERVER.route('/settings', methods=['GET', 'POST'])
def renderSettings():
    """
    Render settings page to configure Floating Tools
    :return: 
    """
    data = {
        'build': FloatingTools.buildData,
        'sources': FloatingTools.sourceData
    }

    # update dashboards env with the latest data.
    for entry in data:
        FloatingTools.Dashboard.setDashboardVariable(entry, data[entry]())

    FloatingTools.branches()
    FloatingTools.releases()

    return render_template('Settings.html', **FloatingTools.Dashboard.dashboardEnv())


@SERVER.route('/settings/_save')
def saveSettings():
    """
    Handles setting saving.
    :return: 
    """

    buildData = FloatingTools.buildData()
    buildData['release'] = request.args.get('release')
    buildData['collaborator'] = False
    if request.args.get('collaborator') == "true":
        buildData['collaborator'] = True
    branch = request.args.get('dev-branch')

    buildData['dev'] = True
    if branch == 'disable':
        buildData['dev'] = False
    buildData['devBranch'] = branch

    FloatingTools.updateBuild(buildData)

    return redirect('/settings')

def settings():
    """
    Launch settings page to configure Floating Tools
    """
    FloatingTools.Dashboard.startServer(url='settings')
