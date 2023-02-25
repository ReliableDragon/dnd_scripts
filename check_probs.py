import argparse
import math

def num_ending(num):
    if num == math.inf:
        return "initith"
    if num in [11, 12, 13]:
        return "th"
    if num % 10 == 1:
        return "st"
    if num % 10 == 2:
        return "nd"
    if num % 10 == 3:
        return "rd"
    return "th"

def success_prob(dc, bonus):
    num_hits = min(20 - dc + 1 + bonus, 20)
    num_misses = 20 - num_hits
    succ_prob = num_hits * 0.05
    return succ_prob

def calculate_stats(dc, bonus):
    # Get prob of success
    prob = success_prob(dc, bonus)
    if prob == 1.0:
        p50, p90, p99, p_fail = 1, 1, 1, math.inf
    else:
        # Num rolls before probability of success is >0.5
        p50 = math.ceil(math.log(0.5, 1-prob))
        # > 0.9
        p90 = math.ceil(math.log(0.1, 1-prob))
        # > 0.99
        p99 = math.ceil(math.log(0.01, 1-prob))
        # Num rolls before a failure is expected
        p_fail = math.log(0.5, prob)
    return prob, p50, p90, p99, p_fail


def check_probs():
    parser = argparse.ArgumentParser(description='Determine what DCs to check.')
    parser.add_argument('--dc', metavar='DC', dest='dc', type=int, nargs='+',
                    help='the dc to make')
    parser.add_argument('--dc_series', metavar='DC Series', dest='dc_series',
                    type=int, nargs='*')
    parser.add_argument('--bonus', dest='bonus', type=int, nargs='?',
                    help='the bonus you want to check for')
    parser.add_argument('--min_bonus', dest='min_bonus', type=int, nargs='?',
                    help='the bonus you want to check for')
    parser.add_argument('--max_bonus', dest='max_bonus', type=int, nargs='?',
                    help='the bonus you want to check for')
    args = parser.parse_args()
    dc = args.dc
    bonus = args.bonus
    min_bonus = args.min_bonus
    max_bonus = args.max_bonus

    if (min_bonus is None) ^ (max_bonus is None):
        raise Exception("You must either set both min_bonus and max_bonus, or set neither.")

    print(f"DC: {dc}\nBonus: {bonus}\nMin Bonus: {min_bonus}\nMax Bonus: {max_bonus}\n")

    if len(dc) == 1:
        dc = dc[0]
        handle_one_dc(dc, bonus, min_bonus, max_bonus)
    else:
        handle_dc_chain(dc, bonus, min_bonus, max_bonus)

def handle_dc_chain(dc_chain, bonus, min_bonus, max_bonus):
    # Calculate stats for the bonus
    if bonus is not None:
        # Get prob of success for whole chain
        prob = 1
        p50 = math.inf
        failures = 0
        for i, dc in enumerate(dc_chain):
            success_chance = calculate_stats(dc, bonus)[0]
            prob *= success_chance
            failures += 1 / success_chance - 1
            if prob < 0.5 and p50 == math.inf:
                p50 = i

        failure_time = f"On average, this check will fail on the {p50+1}{num_ending(p50+1)} attempt (DC {dc_chain[p50]})."
        if p50 == math.inf:
            failure_time = "On average, this check will not fail during this chain."

        print(
           f"The DCs {dc_chain} with a bonus of {'+' if bonus >= 0 else '-'}{bonus} "
           f"has a probability of success of {prob:.2f}.\n"
           f"{failure_time}\n"
           f"On average, this chain will require {failures:.3f} failures to complete.\n"
        )

    if min_bonus is not None:
        min_prob, *_ = calculate_stats(dc, min_bonus)
        max_prob, *_ = calculate_stats(dc, max_bonus)
        # Get prob of success for whole chain
        min_prob = 1
        min_p50 = math.inf
        min_failures = 0
        for i, dc in enumerate(dc_chain):
            min_success_chance = calculate_stats(dc, min_bonus)[0]
            min_prob *= min_success_chance
            min_failures += 1 / min_success_chance - 1
            if min_prob < 0.5 and min_p50 == math.inf:
                min_p50 = i

        max_prob = 1
        max_p50 = math.inf
        max_failures = 0
        for i, dc in enumerate(dc_chain):
            max_success_chance = calculate_stats(dc, max_bonus)[0]
            max_prob *= max_success_chance
            max_failures += 1 / max_success_chance - 1
            if max_prob < 0.5 and max_p50 == math.inf:
                max_p50 = i

        if min_p50 == math.inf:
            failure_time = f"On average, this check will not fail."
        elif max_p50 == math.inf:
            failure_time = (
                f"On average, this check may fail after the "
                f"{min_p50}{num_ending(min_p50+1)} attempt (DC {dc_chain[min_p50]}), or may succeed."
            )
        else:
            failure_time = (
                f"On average, this check will fail between the "
                f"{min_p50+1}{num_ending(min_p50+1)} and "
                f"{max_p50+1}{num_ending(max_p50+1)} attempt (DC {dc_chain[min_p50]}/{dc_chain[max_p50]})."
            )

        print(
           f"The DCs {dc_chain} with a bonus of between "
           f"{'+' if min_bonus >= 0 else '-'}{min_bonus} and {'+' if max_bonus >= 0 else '-'}{max_bonus} "
           f"has a probability of success of between {min_prob:.2f}-{max_prob:.2f}.\n"
           f"{failure_time}\n"
           f"On average, this chain will require between {max_failures:.3f}-{min_failures:.3f} failures to complete."
        )

def handle_one_dc(dc, bonus, min_bonus, max_bonus):
    # Calculate stats for the bonus
    if bonus is not None:
        # Get prob of success
        prob, p50, p90, p99, p_fail = calculate_stats(dc, bonus)

        print(
           f"A DC {dc} check with a bonus of {'+' if bonus >= 0 else '-'}{bonus} "
           f"has a probability of success of {prob:.2f}.\n"
           f"On average, this check will fail every {p_fail:.2f} attempts.\n"
           f"This means the number of turns needed to have a given chance at success are:\n"
           f">50%:\t{p50}\n"
           f">90%:\t{p90}\n"
           f">99%:\t{p99}\n"
        )

    if min_bonus is not None:
        min_prob, min_p50, min_p90, min_p99, min_p_fail = calculate_stats(dc, min_bonus)
        max_prob, max_p50, max_p90, max_p99, max_p_fail = calculate_stats(dc, max_bonus)

        print(
           f"A DC {dc} check with a bonus of between {'+' if bonus >= 0 else '-'}{min_bonus} "
           f"and {'+' if bonus >= 0 else '-'}{max_bonus} has a probability of "
           f"success of between {min_prob:.2f}-{max_prob:.2f}.\n"
           f"On average, this check will fail every {min_p_fail:.2f}-{max_p_fail:.2f} attempts.\n"
           f"This means the number of turns needed to have a given chance at success are:\n"
           f">50%:\t{max_p50}-{min_p50}\n"
           f">90%:\t{max_p90}-{min_p90}\n"
           f">99%:\t{max_p99}-{min_p99}"
        )

if __name__ == "__main__":
    check_probs()
