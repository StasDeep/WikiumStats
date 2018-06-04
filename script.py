from wikium_stats import WikiumStats


def get_creds():
    with open('creds.txt') as outfile:
        return dict(line.strip().split('=', 1) for line in outfile.readlines())

def main():
    creds = get_creds()
    ws = WikiumStats(creds)

    for skill_group in ws.skill_groups:
        print('\n{0} {1} ({2}) {0}'.format('=' * 16, skill_group['title'], skill_group['bpi']))
        for game in skill_group['games']:
            if game['bpi']:
                diff = game['bpi'] - skill_group['bpi']
            else:
                diff = 0

            print('{:>25}: {:4} ({:+d})'.format(game['game']['name'], game['bpi'] or 'None', diff))


if __name__ == '__main__':
    main()
