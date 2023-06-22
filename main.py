import sys, os
sys.path.append('/app/dofunc/packages/bhrtools/bhrteamcal')

from bhrteamcal import BhrTeamCal

if __name__ == '__main__':
    timeoffs_group = os.getenv('TIMEOFFS', 'vac')
    root_path = os.path.dirname(os.path.abspath(__file__))
    bhrtc = BhrTeamCal(timeoffs_group, root_path)
    bhrtc.generate()
