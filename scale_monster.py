import argparse
from math import floor

FRACTIONAL_CRS = [0, 0.125, 0.25, 0.5]
HP_BY_CR = [(1, 6), (7, 35), (36, 49), (50, 70), (71, 85), (86, 100), (101, 115), (116, 130),
            (131, 145), (146, 160), (161, 175), (176, 190), (191, 205), (206, 220), (221, 235),
            (236, 250), (251, 265), (266, 280), (281, 295), (296, 310), (311, 325), (326, 340),
            (341, 355), (356, 400), (401, 445), (446, 490), (491, 535), (536, 580), (581, 625),
            (626, 670), (671, 715), (716, 760), (761, 805), (806, 850)]
HP_OVER_MAX = 45
AC_BY_CR = [13, 13, 13, 13, 13, 13, 13, 14, 15, 15, 15, 16, 16, 17, 17, 17, 18, 18, 18, 18, 19]
AC_OVER_MAX = 0
DMG_BY_CR = [(0, 1), (2, 3), (4, 5), (6, 8), (9, 14), (15, 20), (21, 26), (27, 32), (33, 38),
             (39, 44), (45, 50), (51, 56), (57, 62), (63, 68), (69, 74), (75, 80), (81, 86),
             (87, 92), (93, 98), (99, 104), (105, 110), (111, 116), (117, 122), (123, 140),
             (141, 158), (159, 176), (177, 194), (195, 212), (213, 230), (231, 248), (259, 266),
             (267, 284), (285, 302)]
DMG_OVER_MAX = 17
ATK_BY_CR = [3, 3, 3, 3, 3, 3, 4, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 8, 8, 9, 10, 10, 10, 10, 11, 11,
             11, 12, 12, 12, 13, 13, 13]
CRS_OVER_MAX_PER_ATK = 3
SAVE_BY_CR = [13, 13, 13, 13, 13, 13, 13, 14, 15, 15, 15, 16, 16, 16, 17, 17, 18, 18, 18, 18, 19,
              19, 19, 19, 20, 20, 20, 21, 21, 21, 22, 22, 22]
CRS_OVER_MAX_PER_SAVE = 3

def get_cr(i):
    if i < 0:
        return i
    elif i <= 3:
        return FRACTIONAL_CRS[i]
    else:
        return i - 3

def get_range_frac(n, r):
    return (n - r[0]) / (r[1] - r[0])

def apply_range_frac(n, r):
    return floor((r[1] - r[0]) * n + r[0])

def find_stat_alignment(hp, ac, dmg, atk, save):
    assert hp > 0, 'HP must be positive!'
    i = 0
    while i < len(HP_BY_CR) and HP_BY_CR[i][1] < hp:
        i += 1
    def_cr = i
    if i == len(HP_BY_CR):  # This only happens for CR > 30, so it's okay if it's buggy
        bonus = (hp - HP_BY_CR[-1]) // HP_OVER_MAX
        def_cr += bonus
        def_range_frac = ((hp - HP_BY_CR[-1]) % HP_OVER_MAX) / HP_OVER_MAX
    else:
        def_range_frac = get_range_frac(hp, HP_BY_CR[i])
    cr_by_hp = def_cr
    print(f'HP lines up with CR {get_cr(cr_by_hp)} with range frac {def_range_frac:.2f}.')

    ac_by_cr = AC_BY_CR[def_cr] if def_cr < len(AC_BY_CR) else 19
    cr_by_ac = def_cr
    if ac != ac_by_cr:
        diff = ac - ac_by_cr
        cr_by_ac += diff
        def_cr += diff // 2
    print(f'AC lines up with CR {get_cr(cr_by_ac)}.')
    print(f'Def CR after AC adjustment is {get_cr(def_cr)}.')

    i = 0
    while i < len(DMG_BY_CR) and DMG_BY_CR[i][1] < dmg:
        i += 1
    off_cr = i
    if i == len(DMG_BY_CR):  # This only happens for CR > 30, so it's okay if it's buggy
        bonus = (dmg - DMG_BY_CR[-1]) // DMG_OVER_MAX
        off_cr += bonus
        off_range_frac = ((dmg - DMG_BY_CR[-1]) % DMG_OVER_MAX) / DMG_OVER_MAX
    else:
        off_range_frac = get_range_frac(dmg, DMG_BY_CR[i])
    cr_by_dmg = off_cr
    print(f'DMG lines up with CR {get_cr(cr_by_dmg)} with range frac {off_range_frac:.2f}.')

    cr_by_atk = off_cr
    atk_off_cr = off_cr
    if off_cr < len(ATK_BY_CR):
        atk_by_cr = ATK_BY_CR[off_cr]  
    else:
        atk_by_cr = len(ATK_BY_CR) - 1 + CRS_OVER_MAX_PER_ATK * (off_cr - len(ATK_BY_CR))
    if atk != atk_by_cr:
        diff = atk - atk_by_cr
        cr_by_atk += diff
        atk_off_cr += diff // 2
    print(f'ATK lines up with CR {get_cr(cr_by_atk)}.')
    print(f'Off CR after ATK adjustment is {get_cr(atk_off_cr)}.')

    cr_by_save = off_cr
    save_off_cr = off_cr
    if off_cr < len(SAVE_BY_CR):
        save_by_cr = SAVE_BY_CR[off_cr]  
    else:
        save_by_cr = len(SAVE_BY_CR) - 1 + CRS_OVER_MAX_PER_SAVE * (off_cr - len(SAVE_BY_CR))
    if atk != save_by_cr:
        diff = atk - save_by_cr
        cr_by_save += diff
        save_off_cr += diff // 2
    print(f'SAVE lines up with CR {get_cr(cr_by_save)}.')
    print(f'Off CR after save adjustment is {get_cr(save_off_cr)}.')

    print(f'Using attacks, this should be a CR {get_cr(floor((atk_off_cr + def_cr) / 2 + 0.5))} creature.')
    print(f'Using saves, this should be a CR {get_cr(floor((save_off_cr + def_cr) / 2 + 0.5))} creature.')
    return def_range_frac, off_range_frac, cr_by_hp, cr_by_ac, cr_by_dmg, cr_by_atk, cr_by_save

def scale_stats(cr_diff, cr_by_hp, hp_range_frac, cr_by_ac,
                cr_by_dmg, dmg_range_frac, cr_by_atk, cr_by_save):
    print(f'Adjusting stats by {cr_diff}')
    new_hp_cr = cr_by_hp + cr_diff
    if new_hp_cr < 0:
        hp = 1
    elif new_hp_cr >= len(HP_BY_CR):
        hp = HP_BY_CR[-1] + HP_OVER_MAX * (new_hp_cr - len(HP_BY_CR) - 1) + HP_OVER_MAX * hp_range_frac
    else:
        hp = apply_range_frac(hp_range_frac, HP_BY_CR[new_hp_cr])

    new_ac_cr = cr_by_ac + cr_diff
    if new_ac_cr < 0:
        ac = max(13 + new_ac_cr, 10)
    elif new_ac_cr >= len(AC_BY_CR):
        ac = AC_BY_CR[-1]
    else:
        ac = AC_BY_CR[new_ac_cr]

    new_dmg_cr = cr_by_dmg + cr_diff
    if new_dmg_cr < 0:
        dmg = 0
    elif new_dmg_cr >= len(DMG_BY_CR):
        dmg = DMG_BY_CR[-1] + DMG_OVER_MAX * (new_dmg_cr - len(DMG_BY_CR) - 1) + DMG_OVER_MAX * dmg_range_frac
    else:
        dmg = apply_range_frac(dmg_range_frac, DMG_BY_CR[new_dmg_cr])
    
    new_atk_cr = cr_by_atk + cr_diff
    if new_atk_cr < 0:
        atk = 3
    elif new_atk_cr >= len(ATK_BY_CR):
        atk = ATK_BY_CR[-1] + (new_atk_cr - len(ATK_BY_CR)) / CRS_OVER_MAX_PER_ATK
    else:
        atk = ATK_BY_CR[new_atk_cr]
    
    new_save_cr = cr_by_save + cr_diff
    if new_save_cr < 0:
        save = max(10, 13 + new_save_cr)
    elif new_save_cr >= len(SAVE_BY_CR):
        save = SAVE_BY_CR[-1] + (new_save_cr - len(SAVE_BY_CR)) / CRS_OVER_MAX_PER_SAVE
    else:
        save = SAVE_BY_CR[new_save_cr]

    return hp, ac, dmg, atk, save

def scale_monster(curr_cr, cr, hp, ac, dmg, atk, save):
    curr_cr = FRACTIONAL_CRS.index(curr_cr) if curr_cr in FRACTIONAL_CRS else int(curr_cr + 3)
    cr = FRACTIONAL_CRS.index(cr) if cr in FRACTIONAL_CRS else int(cr + 3)

    hp_range_frac, dmg_range_frac, cr_by_hp, cr_by_ac, cr_by_dmg, cr_by_atk, cr_by_save \
        = find_stat_alignment(hp, ac, dmg, atk, save)
    cr_diff = cr - curr_cr
    new_hp, new_ac, new_dmg, new_atk, new_save = scale_stats(cr_diff, cr_by_hp, hp_range_frac, 
                                                             cr_by_ac, cr_by_dmg, dmg_range_frac,
                                                             cr_by_atk, cr_by_save)
    print(f"""The monster's new stats should be:
HP: {new_hp} (x{new_hp / hp:.2f})
AC: {new_ac}
DMG: {new_dmg} (x{new_dmg / dmg:.2f})
ATK: {new_atk}
SAVE: {new_save}
""")

"""
Arguments: curr_cr, cr, hp, ac, dmg, atk, save
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scale a creature\'s CR.')
    parser.add_argument('curr_cr', type=float, help='the desired cr')
    parser.add_argument('cr', type=float, help='the desired cr')
    parser.add_argument('hp', type=int, help='the creature\'s hp')
    parser.add_argument('ac', type=int, help='the creature\'s ac')
    parser.add_argument('dmg', type=int, help='the creature\'s dmg')
    parser.add_argument('atk', type=int, help='the creature\'s atk bonus')
    parser.add_argument('save', type=int, help='the creature\'s save dc')

    args = parser.parse_args()
    curr_cr = args.curr_cr
    cr = args.cr
    hp = args.hp
    ac = args.ac
    dmg = args.dmg
    atk = args.atk
    save = args.save
    scale_monster(curr_cr, cr, hp, ac, dmg, atk, save)