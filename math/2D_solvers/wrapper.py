import sys
import subprocess
import solve_b
import json
import parse


def parse_singular_points(s: str) -> list:
    """Takes string of singular points generated by M2 as [{a_11, a_21, ..., a_m1}, ..., {a_1n, a_2n, ..., a_mn}]
    and returns a list [(a_1, b_1), ..., (a_n, b_n)]"""
    s = s.replace("[", "")
    s = s.replace("]", "")
    s = s.replace("{", "")
    s = s.replace(",", "")

    # Split string into groups
    s = s.split("}")
    # Last group is always empty
    s = s[:-1]
    # get rid of leading spaces and split tokens
    s = [tuple(v.strip().split(" ")) for v in s]

    return s


def solve(eqn: str) -> dict:
    """Solve for invariants of a 2D curve given as argument."""
    data = {}
    try:
        output = (
            # Run Macaulay2 script (need primary decomposition to get all singular points)
            subprocess.run(
                ["M2", "--script", "./math/2D_solvers/solve_a.m2", eqn],
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        )
    except Exception as e:
        print("An error occurred when trying to run M2:", e)
        return data

    data["eqn"] = eqn
    data["degree"] = int(output[0])
    # No Milnor or Tjurina (returns vector []) => Milnor/Tjurina number is 0
    data["milnor"] = eval(output[1])
    if data["milnor"] == []:
        data["milnor"] = [0]
    data["tjurina"] = eval(output[2])
    if data["tjurina"] == []:
        data["tjurina"] = [0]
    homogenized = output[3]
    singular_points = output[4]
    data["sings"] = solve_b.solve_singularities(parse_singular_points(singular_points))
    data["mults"] = solve_b.solve_multiplicities(homogenized, data["sings"])
    data["arith_genus"] = solve_b.solve_arith_genus(data["degree"])
    data["delta"] = solve_b.solve_delta(data["mults"])
    data["geo_genus"] = solve_b.solve_geo_genus(data["arith_genus"], data["delta"])
    data["branching"] = solve_b.solve_branching(data["milnor"], data["delta"])

    return data


def main():
    try:
        eqn = sys.argv[1]
        # Hacky way to differentiate properly formatted from katie
        if "^" in eqn:
            print(solve(eqn))
        else:
            # parse if from katie's site
            print(solve(parse.parse(eqn)))
    except IndexError:
        print("Enter the equation to solve invariants for.")


if __name__ == "__main__":
    main()