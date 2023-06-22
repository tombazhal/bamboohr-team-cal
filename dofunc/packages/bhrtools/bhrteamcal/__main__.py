from bhrteamcal import BhrTeamCal

def main(args):
    timeoffs_group = args.get("timeoffs", "vac")
    bhrtc = BhrTeamCal(timeoffs_group)
    bhrtc.generate()
    return {"body": "Generation complete."}
