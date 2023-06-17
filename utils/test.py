def make_integer_smaller(big_integer, power_of_ten):
    return big_integer // (10 ** power_of_ten)

# Example usage
big_integer = 6000000000
power_of_ten = 5  # Assuming the specific number is 10^5

smaller_integer = make_integer_smaller(big_integer, power_of_ten)
print(smaller_integer)