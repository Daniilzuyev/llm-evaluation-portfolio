def calculate_cost(input_tokens, output_tokens, model="gpt-4o-mini"):

    pricing = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }

    if model not in pricing:
        raise ValueError(f"Unknown model: {model}")

    input_cost = input_tokens * pricing[model]["input"] / 1_000_000
    output_cost = output_tokens * pricing[model]["output"] / 1_000_000

    return input_cost + output_cost


if __name__ == "__main__":

    cost = calculate_cost(26, 71, "gpt-4o-mini")
    print(f"Cost for 26 input + 71 output tokens: ${cost:.8f}")
    print(f"Cost in cents: {cost * 100:.6f}¢")


    print("\n=== MODEL COMPARISON ===")
    for model in ["gpt-4o-mini", "gpt-4o"]:
        cost = calculate_cost(100, 200, model)
        print(f"{model}: ${cost:.6f}")