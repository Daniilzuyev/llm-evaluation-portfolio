from statsmodels.stats.power import TTestIndPower
import math

# analysis = TTestIndPower()
# n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.8)

def required_sample_size(effect_size: float, alpha: float = 0.05, power: float = 0.8) -> dict:
    analysis = TTestIndPower()
    n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
    n_rounded = math.ceil(n)
    return {
        "required_n_per_group": n_rounded,
        "effect_size": effect_size,
        "alpha": alpha,
        "power": power,
    }

if __name__ == "__main__":
    print(required_sample_size(effect_size=0.5))   # medium effect
    print(required_sample_size(effect_size=0.2))   # small effect
    print(required_sample_size(effect_size=0.8))   # large effect