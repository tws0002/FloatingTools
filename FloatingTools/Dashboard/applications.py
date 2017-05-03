# FloatingTools imports
import FloatingTools

# flask imports
from flask import request, render_template

# package imports
from utilities import SERVER


@SERVER.route('/applications', methods=['GET', 'POST'])
def renderApplications():
    """
    Render applications page
    :return: 
    """
    return render_template('Applications.html', **FloatingTools.Dashboard.dashboardEnv())


def applications():
    """
    Launch applications page
    :return: 
    """
    FloatingTools.Dashboard.startServer(url='applications')
